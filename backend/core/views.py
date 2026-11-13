import csv
import io
import uuid
from django.db import IntegrityError, transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import HttpResponse
from .models import (
    Organization, Location, Contact, Documentation,
    PasswordEntry, Configuration, NetworkDevice, EndpointUser, Server, Peripheral, Software, Backup, VoIP,
    DocumentationVersion, PasswordEntryVersion, ConfigurationVersion,
    OrganizationMember, EntityVersion, AuditLog
)
from .serializers import (
    OrganizationSerializer, LocationSerializer, ContactSerializer,
    DocumentationSerializer, PasswordEntrySerializer, ConfigurationSerializer,
    NetworkDeviceSerializer, EndpointUserSerializer, ServerSerializer, PeripheralSerializer, SoftwareSerializer, BackupSerializer, VoIPSerializer,
    DocumentationVersionSerializer, PasswordEntryVersionSerializer, ConfigurationVersionSerializer,
    EntityVersionSerializer, AuditLogSerializer
)
from .permissions import IsOrganizationMember, IsOrganizationAdmin
from users.utils import get_client_ip as _get_client_ip


def _is_uuid(value):
    """True if value is a valid UUID string."""
    try:
        uuid.UUID(str(value))
        return True
    except (ValueError, TypeError, AttributeError):
        return False


def _get_entity_name(instance):
    """Get a human-readable name for an entity."""
    for attr in ('name', 'title', 'full_name', 'email'):
        val = getattr(instance, attr, None)
        if val:
            return str(val)
    return str(instance.pk)


def _get_org_name(instance):
    """Get the organization name for an entity, if applicable."""
    if isinstance(instance, Organization):
        return instance.name
    org = getattr(instance, 'organization', None)
    if org:
        return org.name
    return ''


class AuditLogMixin:
    """Mixin that automatically logs create, update, and delete actions.

    Place this FIRST in the MRO so its perform_* methods wrap the real ones.
    Captures field-level changes for update actions.
    """

    # Fields that should never appear in audit change data
    SENSITIVE_FIELDS = frozenset({
        'password', 'password_hash', 'secret_key', 'encryption_key',
        'token', 'api_key', 'secret',
    })

    # Internal/meta fields to exclude from change tracking
    EXCLUDED_FIELDS = frozenset({
        'id', 'pk', 'created_at', 'updated_at', 'created_by',
        'deleted_at', 'deleted_by', '_state',
    })

    def _get_trackable_fields(self, instance):
        """Get model field names worth tracking."""
        fields = []
        for f in instance._meta.get_fields():
            if not hasattr(f, 'attname'):
                continue
            name = f.attname
            if name in self.EXCLUDED_FIELDS or name in self.SENSITIVE_FIELDS:
                continue
            fields.append(name)
        return fields

    def _snapshot(self, instance):
        """Take a snapshot of trackable field values."""
        snapshot = {}
        for name in self._get_trackable_fields(instance):
            val = getattr(instance, name, None)
            # Convert non-JSON-serializable types to strings
            if val is not None and not isinstance(val, (str, int, float, bool, list, dict)):
                val = str(val)
            snapshot[name] = val
        return snapshot

    def _compute_diff(self, old_snapshot, new_snapshot):
        """Compute field-level differences between two snapshots."""
        changes = []
        all_keys = set(old_snapshot) | set(new_snapshot)
        for key in sorted(all_keys):
            old_val = old_snapshot.get(key)
            new_val = new_snapshot.get(key)
            if old_val != new_val:
                changes.append({
                    'field': key,
                    'old': old_val,
                    'new': new_val,
                })
        return changes

    def _build_field_summary(self, instance, action):
        """Build field values summary for create/delete actions."""
        snapshot = self._snapshot(instance)
        fields = []
        for key, val in sorted(snapshot.items()):
            if val is not None and val != '':
                fields.append({'field': key, 'value': val})
        return fields

    def _log_action(self, action, instance, changes=None, details=''):
        request = getattr(self, 'request', None)
        if not request:
            return
        entity_type = instance.__class__.__name__
        AuditLog.log(
            user=request.user,
            action=action,
            entity_type=entity_type,
            entity_id=str(instance.pk),
            entity_name=_get_entity_name(instance),
            organization_name=_get_org_name(instance),
            details=details,
            changes=changes,
            ip_address=_get_client_ip(request),
        )

    def after_create(self, instance):
        """Hook for viewsets that need extra work after an object is created."""

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Save the new object (recording who created it), run the viewset's
        after_create hook, and write the audit entry.

        Viewsets must NOT override perform_create - doing so would bypass the
        audit log. Override after_create instead.
        """
        instance = serializer.save(created_by=self.request.user)
        self.after_create(instance)
        fields = self._build_field_summary(instance, 'create')
        self._log_action('create', instance, changes={'fields': fields})

    @transaction.atomic
    def perform_update(self, serializer):
        instance = serializer.instance
        old_snapshot = self._snapshot(instance)
        super().perform_update(serializer)
        instance.refresh_from_db()
        new_snapshot = self._snapshot(instance)
        diff = self._compute_diff(old_snapshot, new_snapshot)
        self._log_action('update', instance, changes={'diff': diff} if diff else None)

    def perform_destroy(self, instance):
        fields = self._build_field_summary(instance, 'delete')
        self._log_action('delete', instance, changes={'fields': fields})
        super().perform_destroy(instance)


class SecureQuerySetMixin:
    """
    Mixin that provides access to organizations for authenticated users.
    All authenticated users can see all organizations (shared workspace model).
    """

    def get_user_organizations(self):
        """Get organizations the current user has access to."""
        # All authenticated users can access all organizations
        return Organization.objects.all()

    def filter_by_organization_access(self, queryset):
        """Filter queryset - all authenticated users have full access."""
        # All authenticated users can see all data
        return queryset


class VersionHistoryMixin:
    """Mixin to add version history functionality to ViewSets."""
    version_model = None  # Must be set in subclass
    version_serializer = None  # Must be set in subclass
    version_fields = []  # Fields to track in versions
    parent_field = None  # Name of the field linking to parent (e.g., 'documentation', 'password_entry')

    def _create_version(self, instance, change_note=''):
        """Create a version snapshot of the current instance."""
        if not self.version_model or not self.parent_field:
            return

        # Get the next version number
        last_version = self.version_model.objects.filter(
            **{self.parent_field: instance}
        ).order_by('-version_number').first()

        next_version = (last_version.version_number + 1) if last_version else 1

        # Create version data from instance
        version_data = {
            self.parent_field: instance,
            'version_number': next_version,
            'created_by': self.request.user if hasattr(self, 'request') else None,
            'change_note': change_note
        }

        # Copy tracked fields
        for field in self.version_fields:
            version_data[field] = getattr(instance, field)

        # Create the version
        self.version_model.objects.create(**version_data)

    def perform_update(self, serializer):
        """Override update to create a version before saving changes."""
        instance = serializer.instance

        # Create version before updating
        change_note = self.request.data.get('change_note', '')
        self._create_version(instance, change_note)

        # Save the update
        updated_instance = serializer.save()

        # Increment version field if it exists (for Documentation and Configuration)
        if hasattr(updated_instance, 'version') and isinstance(getattr(updated_instance, 'version'), int):
            updated_instance.version += 1
            updated_instance.save(update_fields=['version'])

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """Get version history for this entry."""
        instance = self.get_object()
        versions = self.version_model.objects.filter(
            **{self.parent_field: instance}
        ).order_by('-version_number')

        serializer = self.version_serializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='versions/(?P<version_number>[0-9]+)')
    def get_version(self, request, pk=None, version_number=None):
        """Get a specific version."""
        instance = self.get_object()
        try:
            version = self.version_model.objects.get(
                **{self.parent_field: instance, 'version_number': version_number}
            )
            serializer = self.version_serializer(version)
            return Response(serializer.data)
        except self.version_model.DoesNotExist:
            return Response(
                {'detail': 'Version not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], url_path='restore-version/(?P<version_number>[0-9]+)')
    def restore_version(self, request, pk=None, version_number=None):
        """Restore an entry to a specific version."""
        instance = self.get_object()

        try:
            version = self.version_model.objects.get(
                **{self.parent_field: instance, 'version_number': version_number}
            )

            with transaction.atomic():
                # Create a new version of the current state before restoring
                self._create_version(instance, f'Before restoring to version {version_number}')

                # Restore fields from version
                for field in self.version_fields:
                    setattr(instance, field, getattr(version, field))

                instance.save()

                # Create a new version after restoring
                self._create_version(instance, f'Restored from version {version_number}')

                if hasattr(self, '_log_action'):
                    self._log_action(
                        'restore', instance,
                        details=f'Restored to version {version_number}'
                    )

            serializer = self.get_serializer(instance)
            return Response({
                'detail': f'Successfully restored to version {version_number}',
                'data': serializer.data
            })

        except self.version_model.DoesNotExist:
            return Response(
                {'detail': 'Version not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class SoftDeleteViewSetMixin:
    """Mixin to add soft delete functionality to ViewSets."""

    @staticmethod
    def _parent_organization_deleted(instance):
        """True if the instance belongs to an organization that is itself soft-deleted."""
        if isinstance(instance, Organization):
            return False
        org_id = getattr(instance, 'organization_id', None)
        if not org_id:
            return False
        return Organization.all_objects.filter(pk=org_id, deleted_at__isnull=False).exists()

    def destroy(self, request, *args, **kwargs):
        """Override destroy to perform soft delete instead of hard delete."""
        instance = self.get_object()
        with transaction.atomic():
            # Audit log the delete action (with a snapshot of what was deleted)
            if hasattr(self, '_log_action'):
                fields = self._build_field_summary(instance, 'delete')
                self._log_action('delete', instance, changes={'fields': fields})
            instance.delete(user=request.user)
        return Response(
            {'detail': 'Item moved to deleted items. You can restore it from the Deleted Items section.'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore a soft-deleted item."""
        # Get the object from all_objects manager (includes deleted)
        model_class = self.get_queryset().model
        try:
            instance = model_class.all_objects.get(pk=pk)
        except (model_class.DoesNotExist, ValueError, DjangoValidationError):
            return Response({'detail': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not instance.is_deleted:
            return Response(
                {'detail': 'Item is not deleted.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if self._parent_organization_deleted(instance):
            return Response(
                {'detail': 'This item belongs to a deleted organization. Restore the organization first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            with transaction.atomic():
                instance.restore()
                # Audit log the restore action
                if hasattr(self, '_log_action'):
                    self._log_action('restore', instance)
        except IntegrityError:
            return Response(
                {'detail': 'Cannot restore: an active item with the same name already exists. '
                           'Rename or delete that item first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(instance)
        return Response(
            {'detail': 'Item restored successfully.', 'data': serializer.data},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def deleted(self, request):
        """Get all soft-deleted items."""
        model_class = self.get_queryset().model
        deleted_items = model_class.objects.deleted()

        related = [
            f for f in ('organization', 'location', 'created_by', 'deleted_by')
            if f in {field.name for field in model_class._meta.fields}
        ]
        if related:
            deleted_items = deleted_items.select_related(*related)

        if hasattr(model_class, 'organization'):
            # Items that were removed as part of deleting their organization are
            # restored together with it, so they are not listed individually.
            deleted_items = deleted_items.filter(organization__deleted_at__isnull=True)

            # Apply additional organization filter if provided
            org_id = request.query_params.get('organization_id')
            if org_id:
                if not _is_uuid(org_id):
                    return Response({'detail': 'Invalid organization_id.'}, status=status.HTTP_400_BAD_REQUEST)
                deleted_items = deleted_items.filter(organization_id=org_id)

        page = self.paginate_queryset(deleted_items)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(deleted_items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['delete'])
    def hard_delete(self, request, pk=None):
        """Permanently delete an item (admin only)."""
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only administrators can permanently delete items.'},
                status=status.HTTP_403_FORBIDDEN
            )

        model_class = self.get_queryset().model
        try:
            instance = model_class.all_objects.get(pk=pk)
        except (model_class.DoesNotExist, ValueError, DjangoValidationError):
            return Response({'detail': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            if hasattr(self, '_log_action'):
                self._log_action('delete', instance, details='Permanently deleted')
            instance.hard_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrganizationFilterMixin:
    """Mixin to add organization and location filtering to ViewSets."""

    @action(detail=False, methods=['get'])
    def by_organization(self, request):
        """Filter items by organization."""
        org_id = request.query_params.get('organization_id')
        if org_id and _is_uuid(org_id):
            queryset = self.get_queryset().filter(organization_id=org_id)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response(
            {'detail': 'A valid organization_id is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )


class LocationFilterMixin(OrganizationFilterMixin):
    """Mixin for viewsets that also support location filtering."""

    @action(detail=False, methods=['get'])
    def by_location(self, request):
        """Filter items by location."""
        location_id = request.query_params.get('location_id')
        if location_id and _is_uuid(location_id):
            queryset = self.get_queryset().filter(location_id=location_id)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response(
            {'detail': 'A valid location_id is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )


class CSVImportMixin:
    """
    Shared CSV import logic. Each row is validated through the viewset's
    serializer, so imported data obeys the same rules as data entered in the UI.
    """
    CSV_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    CSV_MAX_ROWS = 10000

    def _csv_row_to_data(self, row, organization):
        """Convert a CSV row (dict) to serializer input. Implemented by the viewset."""
        raise NotImplementedError

    def _run_csv_import(self, request, label):
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        csv_file = request.FILES['file']
        if csv_file.size > self.CSV_MAX_FILE_SIZE:
            return Response({'error': 'File size exceeds 5MB limit'}, status=status.HTTP_400_BAD_REQUEST)
        if not csv_file.name.lower().endswith('.csv'):
            return Response({'error': 'File must be a CSV'}, status=status.HTTP_400_BAD_REQUEST)

        org_id = request.data.get('organization_id')
        if not org_id:
            return Response({'error': 'organization_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        organization = Organization.objects.filter(id=org_id).first() if _is_uuid(org_id) else None
        if organization is None:
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # utf-8-sig handles the BOM that Excel adds to exported CSV files
            decoded_file = csv_file.read().decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(decoded_file))
            rows = list(reader)
        except (UnicodeDecodeError, csv.Error):
            return Response(
                {'error': 'Could not read the file. Make sure it is a UTF-8 encoded CSV.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_count = 0
        errors = []
        for row_num, row in enumerate(rows, start=2):  # row 1 is the header
            if row_num > self.CSV_MAX_ROWS + 1:
                errors.append({'row': row_num, 'error': f'Exceeded maximum row limit of {self.CSV_MAX_ROWS}'})
                break
            # Skip completely empty lines
            if not any((v or '').strip() for v in row.values() if isinstance(v, str)):
                continue
            try:
                data = self._csv_row_to_data(row, organization)
                serializer = self.get_serializer(data=data)
                if not serializer.is_valid():
                    messages = []
                    for field, field_errors in serializer.errors.items():
                        if not isinstance(field_errors, (list, tuple)):
                            field_errors = [field_errors]
                        text = ' '.join(str(e) for e in field_errors)
                        messages.append(text if field == 'non_field_errors' else f'{field}: {text}')
                    errors.append({'row': row_num, 'error': '; '.join(messages)})
                    continue
                with transaction.atomic():
                    serializer.save(created_by=request.user)
                created_count += 1
            except IntegrityError:
                errors.append({'row': row_num, 'error': 'Duplicate of an existing record'})
            except Exception:
                errors.append({'row': row_num, 'error': 'Could not import this row'})

        if created_count:
            AuditLog.log(
                user=request.user,
                action='import',
                entity_type=self.get_queryset().model.__name__,
                entity_name=csv_file.name,
                organization_name=organization.name,
                details=f'CSV import: {created_count} created, {len(errors)} row(s) with errors',
                ip_address=_get_client_ip(request),
            )

        response_data = {'created': created_count, 'errors': errors}
        if errors:
            response_data['message'] = f'Imported {created_count} {label} with {len(errors)} errors'
        else:
            response_data['message'] = f'Successfully imported {created_count} {label}'
        return Response(response_data, status=status.HTTP_201_CREATED)


def _csv_value(row, key, max_length):
    """Read a CSV cell as a trimmed, length-limited string."""
    return (row.get(key) or '').strip()[:max_length]



class OrganizationViewSet(AuditLogMixin, SecureQuerySetMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Organization CRUD operations."""
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['is_active', 'country']
    search_fields = ['name', 'description', 'email']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """Return only organizations the user has access to."""
        queryset = Organization.objects.select_related('created_by', 'deleted_by')
        return self.filter_by_organization_access(queryset)

    def after_create(self, org):
        """Add the creator as owner and create the default location."""
        # Automatically add creator as organization owner
        OrganizationMember.objects.create(
            organization=org,
            user=self.request.user,
            role='owner',
            created_by=self.request.user
        )
        # Automatically create a default "Head Office" location if address is provided
        # Location requires: address, city, postal_code, country
        if org.address and org.city and org.postal_code and org.country:
            Location.objects.create(
                organization=org,
                name='Head Office',
                address=org.address,
                city=org.city,
                state_province=org.state_province,
                postal_code=org.postal_code,
                country=org.country,
                phone=org.phone,
                created_by=self.request.user
            )

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if query:
            # Security: Only search within accessible organizations
            organizations = self.get_queryset().filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(email__icontains=query)
            )
            serializer = self.get_serializer(organizations, many=True)
            return Response(serializer.data)
        return Response([])

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        organization = self.get_object()
        return Response({
            'organization': organization.name,
            'locations_count': organization.locations.count(),
            'contacts_count': organization.contacts.count(),
            'documentations_count': organization.documentations.count(),
            'password_entries_count': organization.password_entries.count(),
            'configurations_count': organization.configurations.count(),
        })


class LocationViewSet(AuditLogMixin, SecureQuerySetMixin, OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Location CRUD operations."""
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['organization', 'is_active', 'country']
    search_fields = ['name', 'city', 'address']
    ordering_fields = ['name', 'city', 'created_at']
    ordering = ['organization', 'name']

    def get_queryset(self):
        """Return only locations from organizations the user has access to."""
        queryset = Location.objects.select_related('organization', 'created_by', 'deleted_by')
        return self.filter_by_organization_access(queryset)



class ContactViewSet(AuditLogMixin, SecureQuerySetMixin, CSVImportMixin, LocationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Contact CRUD operations."""
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['organization', 'location', 'is_active']
    search_fields = ['first_name', 'last_name', 'email', 'title']
    ordering_fields = ['last_name', 'first_name', 'created_at']
    ordering = ['organization', 'last_name', 'first_name']

    def get_queryset(self):
        """Return only contacts from organizations the user has access to."""
        queryset = Contact.objects.select_related('organization', 'location', 'created_by', 'deleted_by')
        return self.filter_by_organization_access(queryset)


    @action(detail=False, methods=['get'])
    def download_example_csv(self, request):
        """Download an example CSV file for contact imports."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="contacts_example.csv"'

        writer = csv.writer(response)
        # Write header
        writer.writerow(['first_name', 'last_name', 'title', 'email', 'phone'])
        # Write example rows
        writer.writerow(['John', 'Doe', 'IT Manager', 'john.doe@example.com', '+1-555-0100'])
        writer.writerow(['Jane', 'Smith', 'HR Director', 'jane.smith@example.com', '+1-555-0200'])
        writer.writerow(['Bob', 'Johnson', 'CEO', 'bob.johnson@example.com', '+1-555-0300'])

        return response

    def _csv_row_to_data(self, row, organization):
        # Imported contacts go to the organization's first (oldest) location, if any
        default_location = getattr(self, '_csv_default_location', None)
        return {
            'organization': str(organization.id),
            'location': str(default_location.id) if default_location else None,
            'first_name': _csv_value(row, 'first_name', 100),
            'last_name': _csv_value(row, 'last_name', 100),
            'title': _csv_value(row, 'title', 100),
            'email': _csv_value(row, 'email', 254),
            'phone': _csv_value(row, 'phone', 20),
            'is_active': True,
        }

    @action(detail=False, methods=['post'])
    def import_csv(self, request):
        """Import contacts from a CSV file."""
        org_id = request.data.get('organization_id')
        self._csv_default_location = (
            Location.objects.filter(organization_id=org_id).order_by('created_at').first()
            if _is_uuid(org_id) else None
        )
        return self._run_csv_import(request, 'contacts')


class DocumentationViewSet(AuditLogMixin, SecureQuerySetMixin, OrganizationFilterMixin, VersionHistoryMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Documentation CRUD operations."""
    serializer_class = DocumentationSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['organization', 'category', 'is_published']
    search_fields = ['title', 'content', 'tags']
    ordering_fields = ['title', 'created_at', 'category']
    ordering = ['-created_at']

    # Version history configuration
    version_model = DocumentationVersion
    version_serializer = DocumentationVersionSerializer
    version_fields = ['title', 'content', 'category', 'tags', 'is_published']
    parent_field = 'documentation'

    def get_queryset(self):
        """Return only documentation from organizations the user has access to."""
        queryset = Documentation.objects.select_related('organization', 'created_by', 'deleted_by')
        return self.filter_by_organization_access(queryset)

    def after_create(self, instance):
        # Create initial version on create
        self._create_version(instance, 'Initial version')

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        documentation = self.get_object()
        documentation.is_published = True
        documentation.save(update_fields=['is_published', 'updated_at'])
        self._log_action('update', documentation, changes={'diff': [
            {'field': 'is_published', 'old': False, 'new': True}
        ]})
        return Response({'status': 'documentation published'})

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        documentation = self.get_object()
        documentation.is_published = False
        documentation.save(update_fields=['is_published', 'updated_at'])
        self._log_action('update', documentation, changes={'diff': [
            {'field': 'is_published', 'old': True, 'new': False}
        ]})
        return Response({'status': 'documentation unpublished'})


class PasswordEntryViewSet(AuditLogMixin, SecureQuerySetMixin, OrganizationFilterMixin, VersionHistoryMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for PasswordEntry CRUD operations."""
    serializer_class = PasswordEntrySerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['organization', 'category']
    search_fields = ['name', 'username', 'url']
    ordering_fields = ['name', 'category', 'created_at']
    ordering = ['organization', 'name']

    # Version history configuration
    version_model = PasswordEntryVersion
    version_serializer = PasswordEntryVersionSerializer
    version_fields = ['name', 'username', 'password', 'url', 'notes', 'category', 'is_encrypted']
    parent_field = 'password_entry'

    def get_queryset(self):
        """Return only password entries from organizations the user has access to."""
        queryset = PasswordEntry.objects.select_related('organization', 'created_by', 'deleted_by')
        return self.filter_by_organization_access(queryset)

    def after_create(self, instance):
        # Create initial version on create
        self._create_version(instance, 'Initial version')

    @action(detail=True, methods=['post'])
    def retrieve_password(self, request, pk=None):
        """
        Securely retrieve the decrypted password.
        This action logs password access for audit purposes.
        """
        import logging
        from .encryption import decrypt_password

        security_logger = logging.getLogger('security')

        password_entry = self.get_object()

        # Log password access for audit trail
        security_logger.info(
            f"Password retrieved: user={request.user.email}, "
            f"password_entry={password_entry.id}, "
            f"name={password_entry.name}, "
            f"organization={password_entry.organization.name}, "
            f"ip={_get_client_ip(request) or 'unknown'}"
        )
        # Also record it in the in-app audit log so admins can see who viewed what
        self._log_action('view', password_entry, details='Password revealed')

        try:
            decrypted_password = decrypt_password(password_entry.password)
            return Response({
                'password': decrypted_password,
                'warning': 'This password was retrieved securely. Access has been logged.'
            })
        except Exception as e:
            security_logger.error(
                f"Password decryption failed: user={request.user.email}, "
                f"password_entry={password_entry.id}, error={str(e)}"
            )
            return Response(
                {'error': 'Failed to retrieve password'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConfigurationViewSet(AuditLogMixin, SecureQuerySetMixin, OrganizationFilterMixin, VersionHistoryMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Configuration CRUD operations."""
    serializer_class = ConfigurationSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['organization', 'config_type', 'is_active']
    search_fields = ['name', 'description', 'content']
    ordering_fields = ['name', 'config_type', 'created_at']
    ordering = ['organization', 'config_type', 'name']

    # Version history configuration
    version_model = ConfigurationVersion
    version_serializer = ConfigurationVersionSerializer
    version_fields = ['name', 'config_type', 'content', 'description', 'version', 'is_active']
    parent_field = 'configuration'

    def get_queryset(self):
        """Return only configurations from organizations the user has access to."""
        queryset = Configuration.objects.select_related('organization', 'created_by', 'deleted_by')
        return self.filter_by_organization_access(queryset)

    def after_create(self, instance):
        # Create initial version on create
        self._create_version(instance, 'Initial version')


class NetworkDeviceViewSet(AuditLogMixin, SecureQuerySetMixin, OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for NetworkDevice CRUD operations."""
    serializer_class = NetworkDeviceSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['organization', 'device_type', 'location', 'is_active']
    search_fields = ['name', 'manufacturer', 'model', 'ip_address']
    ordering_fields = ['name', 'device_type', 'created_at']
    ordering = ['organization', 'device_type', 'name']

    def get_queryset(self):
        """Return only network devices from organizations the user has access to."""
        queryset = NetworkDevice.objects.select_related('organization', 'location', 'created_by', 'deleted_by').prefetch_related('internet_connections')
        return self.filter_by_organization_access(queryset)



class EndpointUserViewSet(AuditLogMixin, SecureQuerySetMixin, CSVImportMixin, OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for EndpointUser CRUD operations."""
    serializer_class = EndpointUserSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['organization', 'device_type', 'assigned_to', 'location', 'is_active']
    search_fields = ['name', 'manufacturer', 'model', 'hostname', 'ip_address']
    ordering_fields = ['name', 'device_type', 'created_at']
    ordering = ['organization', 'device_type', 'name']

    def get_queryset(self):
        """Return only endpoint users from organizations the user has access to."""
        queryset = EndpointUser.objects.select_related('organization', 'location', 'assigned_to', 'created_by', 'deleted_by')
        return self.filter_by_organization_access(queryset)


    @action(detail=False, methods=['get'])
    def download_example_csv(self, request):
        """Download an example CSV file for endpoint user imports."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="endpoint_users_example.csv"'

        writer = csv.writer(response)
        # Write header
        writer.writerow(['name', 'device_type', 'manufacturer', 'model', 'cpu', 'ram', 'storage', 'gpu', 'operating_system', 'ip_address', 'mac_address', 'hostname', 'serial_number'])
        # Write example rows
        writer.writerow(['DESKTOP-001', 'desktop', 'Dell', 'OptiPlex 7090', 'Intel Core i7-11700', '16GB DDR4', '512GB SSD', 'Intel UHD 750', 'Windows 11 Pro', '192.168.1.101', 'AA:BB:CC:DD:EE:01', 'desktop-001', 'ABC123456'])
        writer.writerow(['LAPTOP-002', 'laptop', 'Lenovo', 'ThinkPad X1 Carbon', 'Intel Core i7-1165G7', '16GB DDR4', '1TB SSD', 'Intel Iris Xe', 'Windows 11 Pro', '192.168.1.102', 'AA:BB:CC:DD:EE:02', 'laptop-002', 'DEF789012'])
        writer.writerow(['WORKSTATION-003', 'workstation', 'HP', 'Z4 G4', 'Intel Xeon W-2245', '64GB DDR4', '2TB NVMe SSD', 'NVIDIA Quadro RTX 4000', 'Windows 10 Pro', '192.168.1.103', 'AA:BB:CC:DD:EE:03', 'workstation-003', 'GHI345678'])

        return response

    def _csv_row_to_data(self, row, organization):
        device_type = _csv_value(row, 'device_type', 50).lower() or 'desktop'
        if device_type not in ('desktop', 'laptop', 'workstation', 'other'):
            device_type = 'other'
        return {
            'organization': str(organization.id),
            'name': _csv_value(row, 'name', 255),
            'device_type': device_type,
            'manufacturer': _csv_value(row, 'manufacturer', 255),
            'model': _csv_value(row, 'model', 255),
            'cpu': _csv_value(row, 'cpu', 255),
            'ram': _csv_value(row, 'ram', 100),
            'storage': _csv_value(row, 'storage', 255),
            'gpu': _csv_value(row, 'gpu', 255),
            'operating_system': _csv_value(row, 'operating_system', 255),
            'ip_address': _csv_value(row, 'ip_address', 50),
            'mac_address': _csv_value(row, 'mac_address', 50),
            'hostname': _csv_value(row, 'hostname', 255),
            'serial_number': _csv_value(row, 'serial_number', 255),
            'is_active': True,
        }

    @action(detail=False, methods=['post'])
    def import_csv(self, request):
        """Import endpoint users from a CSV file."""
        return self._run_csv_import(request, 'endpoint users')


class ServerViewSet(AuditLogMixin, SecureQuerySetMixin, OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Server CRUD operations."""
    serializer_class = ServerSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['organization', 'server_type', 'location', 'is_active']
    search_fields = ['name', 'role', 'manufacturer', 'model', 'hostname', 'ip_address']
    ordering_fields = ['name', 'server_type', 'created_at']
    ordering = ['organization', 'server_type', 'name']

    def get_queryset(self):
        """Return only servers from organizations the user has access to."""
        queryset = Server.objects.select_related('organization', 'location', 'host_server', 'created_by', 'deleted_by')
        return self.filter_by_organization_access(queryset)



class PeripheralViewSet(AuditLogMixin, SecureQuerySetMixin, OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Peripheral CRUD operations."""
    serializer_class = PeripheralSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['organization', 'device_type', 'location', 'is_active']
    search_fields = ['name', 'manufacturer', 'model', 'ip_address']
    ordering_fields = ['name', 'device_type', 'created_at']
    ordering = ['organization', 'device_type', 'name']

    def get_queryset(self):
        """Return only peripherals from organizations the user has access to."""
        queryset = Peripheral.objects.select_related('organization', 'location', 'created_by', 'deleted_by')
        return self.filter_by_organization_access(queryset)



class SoftwareViewSet(AuditLogMixin, SecureQuerySetMixin, OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Software CRUD operations."""
    serializer_class = SoftwareSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['organization', 'software_type', 'license_type', 'is_active']
    search_fields = ['name', 'vendor', 'license_key']
    ordering_fields = ['name', 'software_type', 'expiry_date', 'created_at']
    ordering = ['organization', 'software_type', 'name']

    def get_queryset(self):
        """Return only software from organizations the user has access to."""
        queryset = Software.objects.select_related('organization', 'created_by', 'deleted_by').prefetch_related(
            'software_assignments__contact',
            'software_assignments__created_by'
        )
        return self.filter_by_organization_access(queryset)



class BackupViewSet(AuditLogMixin, SecureQuerySetMixin, OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Backup CRUD operations."""
    serializer_class = BackupSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['organization', 'backup_type', 'backup_status', 'location', 'is_active']
    search_fields = ['name', 'vendor', 'target_systems', 'storage_location']
    ordering_fields = ['name', 'backup_type', 'last_backup_date', 'created_at']
    ordering = ['organization', 'backup_type', 'name']

    def get_queryset(self):
        """Return only backups from organizations the user has access to."""
        queryset = Backup.objects.select_related('organization', 'location', 'created_by', 'deleted_by')
        return self.filter_by_organization_access(queryset)



class VoIPViewSet(AuditLogMixin, SecureQuerySetMixin, OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for VoIP CRUD operations."""
    serializer_class = VoIPSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['organization', 'voip_type', 'license_type', 'is_active']
    search_fields = ['name', 'vendor', 'license_key']
    ordering_fields = ['name', 'voip_type', 'expiry_date', 'created_at']
    ordering = ['organization', 'voip_type', 'name']

    def get_queryset(self):
        """Return only VoIP from organizations the user has access to."""
        queryset = VoIP.objects.select_related('organization', 'created_by', 'deleted_by').prefetch_related(
            'voip_assignments__contact',
            'voip_assignments__created_by'
        )
        return self.filter_by_organization_access(queryset)



class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only viewset for audit logs. Admin only."""
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_fields = ['action', 'entity_type', 'user']
    search_fields = ['entity_name', 'entity_type', 'details', 'user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['timestamp', 'action', 'entity_type']
    ordering = ['-timestamp']

    def get_queryset(self):
        return AuditLog.objects.select_related('user').all()
