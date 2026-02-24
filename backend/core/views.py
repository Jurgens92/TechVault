import csv
import io
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.http import HttpResponse
from .models import (
    Organization, Location, Contact, Documentation,
    PasswordEntry, Configuration, NetworkDevice, EndpointUser, Server, Peripheral, Software, Backup, VoIP,
    DocumentationVersion, PasswordEntryVersion, ConfigurationVersion,
    OrganizationMember, EntityVersion
)
from .serializers import (
    OrganizationSerializer, LocationSerializer, ContactSerializer,
    DocumentationSerializer, PasswordEntrySerializer, ConfigurationSerializer,
    NetworkDeviceSerializer, EndpointUserSerializer, ServerSerializer, PeripheralSerializer, SoftwareSerializer, BackupSerializer, VoIPSerializer,
    DocumentationVersionSerializer, PasswordEntryVersionSerializer, ConfigurationVersionSerializer,
    EntityVersionSerializer
)
from .permissions import IsOrganizationMember, IsOrganizationAdmin


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
        instance = self.get_object()

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

            # Create a new version of the current state before restoring
            self._create_version(instance, f'Before restoring to version {version_number}')

            # Restore fields from version
            for field in self.version_fields:
                setattr(instance, field, getattr(version, field))

            instance.save()

            # Create a new version after restoring
            self._create_version(instance, f'Restored from version {version_number}')

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


class UnifiedVersionHistoryMixin:
    """
    Mixin to add version history using the unified EntityVersion model.

    This is the Single Source of Truth for version history, replacing the
    per-entity version tables (DocumentationVersion, PasswordEntryVersion, etc.).

    Usage:
        class MyViewSet(UnifiedVersionHistoryMixin, viewsets.ModelViewSet):
            use_unified_versioning = True  # Enable unified versioning
    """
    use_unified_versioning = True

    def _create_unified_version(self, instance, change_note=''):
        """Create a version snapshot using the unified EntityVersion model."""
        user = self.request.user if hasattr(self, 'request') else None
        EntityVersion.create_version(
            instance,
            user=user,
            change_note=change_note,
            serializer_class=self.get_serializer_class()
        )

    def perform_create(self, serializer):
        """Create initial version on entity creation."""
        instance = serializer.save(created_by=self.request.user)
        if self.use_unified_versioning:
            self._create_unified_version(instance, 'Initial version')

    def perform_update(self, serializer):
        """Create version before updating entity."""
        instance = self.get_object()

        # Create version of current state before updating
        if self.use_unified_versioning:
            change_note = self.request.data.get('change_note', '')
            self._create_unified_version(instance, change_note)

        # Save the update
        updated_instance = serializer.save()

        # Increment version field if it exists
        if hasattr(updated_instance, 'version') and isinstance(getattr(updated_instance, 'version'), int):
            updated_instance.version += 1
            updated_instance.save(update_fields=['version'])

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """Get version history for this entry using unified versioning."""
        instance = self.get_object()
        versions = EntityVersion.get_versions(instance)
        serializer = EntityVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='versions/(?P<version_number>[0-9]+)')
    def get_version(self, request, pk=None, version_number=None):
        """Get a specific version."""
        instance = self.get_object()
        version = EntityVersion.get_version(instance, int(version_number))
        if not version:
            return Response(
                {'detail': 'Version not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = EntityVersionSerializer(version)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='restore-version/(?P<version_number>[0-9]+)')
    def restore_version(self, request, pk=None, version_number=None):
        """Restore an entry to a specific version."""
        instance = self.get_object()
        version = EntityVersion.get_version(instance, int(version_number))

        if not version:
            return Response(
                {'detail': 'Version not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Create a new version of current state before restoring
            self._create_unified_version(instance, f'Before restoring to version {version_number}')

            # Restore fields from snapshot
            snapshot = version.snapshot
            for field_name, value in snapshot.items():
                if hasattr(instance, field_name) and field_name not in ['id', 'pk', 'created_at', 'created_by', 'organization', 'organization_name']:
                    try:
                        setattr(instance, field_name, value)
                    except (AttributeError, TypeError):
                        pass

            instance.save()

            # Create a version for the restored state
            self._create_unified_version(instance, f'Restored from version {version_number}')

            serializer = self.get_serializer(instance)
            return Response({
                'detail': f'Successfully restored to version {version_number}',
                'data': serializer.data
            })
        except Exception:
            return Response(
                {'detail': 'Error restoring version. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SoftDeleteViewSetMixin:
    """Mixin to add soft delete functionality to ViewSets."""

    def _check_organization_access(self, instance):
        """Check if user has access to the instance's organization."""
        user = self.request.user
        if user.is_superuser:
            return True

        # Get organization from instance
        if isinstance(instance, Organization):
            org = instance
        elif hasattr(instance, 'organization'):
            org = instance.organization
        else:
            return True  # No organization relationship

        return OrganizationMember.user_has_access(user, org)

    def destroy(self, request, *args, **kwargs):
        """Override destroy to perform soft delete instead of hard delete."""
        instance = self.get_object()
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

            # Security: Check organization access
            if not self._check_organization_access(instance):
                return Response(
                    {'detail': 'You do not have access to this item.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            if not instance.is_deleted:
                return Response(
                    {'detail': 'Item is not deleted.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            instance.restore()
            serializer = self.get_serializer(instance)
            return Response(
                {'detail': 'Item restored successfully.', 'data': serializer.data},
                status=status.HTTP_200_OK
            )
        except model_class.DoesNotExist:
            return Response(
                {'detail': 'Item not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def deleted(self, request):
        """Get all soft-deleted items."""
        model_class = self.get_queryset().model
        deleted_items = model_class.objects.deleted()

        # Security: Filter by user's accessible organizations
        if hasattr(self, 'filter_by_organization_access'):
            deleted_items = self.filter_by_organization_access(deleted_items)

        # Apply additional organization filter if provided
        org_id = request.query_params.get('organization_id')
        if org_id and hasattr(model_class, 'organization'):
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

            # Security: Check organization access
            if not self._check_organization_access(instance):
                return Response(
                    {'detail': 'You do not have access to this item.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            instance.hard_delete()
            return Response(
                {'detail': 'Item permanently deleted.'},
                status=status.HTTP_204_NO_CONTENT
            )
        except model_class.DoesNotExist:
            return Response(
                {'detail': 'Item not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class OrganizationFilterMixin:
    """Mixin to add organization and location filtering to ViewSets."""

    @action(detail=False, methods=['get'])
    def by_organization(self, request):
        """Filter items by organization."""
        org_id = request.query_params.get('organization_id')
        if org_id:
            queryset = self.get_queryset().filter(organization_id=org_id)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response([], status=status.HTTP_400_BAD_REQUEST)


class LocationFilterMixin(OrganizationFilterMixin):
    """Mixin for viewsets that also support location filtering."""

    @action(detail=False, methods=['get'])
    def by_location(self, request):
        """Filter items by location."""
        location_id = request.query_params.get('location_id')
        if location_id:
            queryset = self.get_queryset().filter(location_id=location_id)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response([], status=status.HTTP_400_BAD_REQUEST)


class OrganizationViewSet(SecureQuerySetMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Organization CRUD operations."""
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['is_active', 'country']
    search_fields = ['name', 'description', 'email']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """Return only organizations the user has access to."""
        queryset = Organization.objects.all()
        return self.filter_by_organization_access(queryset)

    def perform_create(self, serializer):
        """Create organization and add creator as owner."""
        org = serializer.save(created_by=self.request.user)
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


class LocationViewSet(SecureQuerySetMixin, OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Location CRUD operations."""
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['organization', 'is_active', 'country']
    search_fields = ['name', 'city', 'address']
    ordering_fields = ['name', 'city', 'created_at']
    ordering = ['organization', 'name']

    def get_queryset(self):
        """Return only locations from organizations the user has access to."""
        queryset = Location.objects.select_related('organization')
        return self.filter_by_organization_access(queryset)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ContactViewSet(SecureQuerySetMixin, LocationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Contact CRUD operations."""
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['organization', 'location', 'is_active']
    search_fields = ['first_name', 'last_name', 'email', 'title']
    ordering_fields = ['last_name', 'first_name', 'created_at']
    ordering = ['organization', 'last_name', 'first_name']

    def get_queryset(self):
        """Return only contacts from organizations the user has access to."""
        queryset = Contact.objects.select_related('organization', 'location')
        return self.filter_by_organization_access(queryset)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

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

    @action(detail=False, methods=['post'])
    def import_csv(self, request):
        """Import contacts from a CSV file."""
        # Security: File size limit (5MB max)
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
        MAX_ROWS = 10000

        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        csv_file = request.FILES['file']

        # Security: Check file size
        if csv_file.size > MAX_FILE_SIZE:
            return Response(
                {'error': 'File size exceeds 5MB limit'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check file extension
        if not csv_file.name.endswith('.csv'):
            return Response(
                {'error': 'File must be a CSV'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get organization_id from request
        org_id = request.data.get('organization_id')
        if not org_id:
            return Response(
                {'error': 'organization_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify organization exists and user has access
        try:
            organization = Organization.objects.get(id=org_id)
            # Security: Check user has access to this organization
            if not OrganizationMember.user_has_access(request.user, organization) and not request.user.is_superuser:
                return Response(
                    {'error': 'You do not have access to this organization'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Organization.DoesNotExist:
            return Response(
                {'error': 'Organization not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get the default location for this organization (oldest/first created)
        default_location = Location.objects.filter(
            organization=organization,
            deleted_at__isnull=True
        ).order_by('created_at').first()

        # Read and decode CSV file
        try:
            # Use utf-8-sig to handle BOM (Byte Order Mark) from Excel-exported CSV files
            decoded_file = csv_file.read().decode('utf-8-sig')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            created_count = 0
            errors = []

            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                # Security: Limit number of rows
                if row_num > MAX_ROWS + 1:
                    errors.append({
                        'row': row_num,
                        'error': f'Exceeded maximum row limit of {MAX_ROWS}'
                    })
                    break

                try:
                    # Security: Sanitize inputs - strip and limit length
                    first_name = row.get('first_name', '').strip()[:100]
                    last_name = row.get('last_name', '').strip()[:100]
                    title = row.get('title', '').strip()[:100]
                    email = row.get('email', '').strip()[:254]
                    phone = row.get('phone', '').strip()[:20]

                    # Create contact with default location if available
                    Contact.objects.create(
                        organization=organization,
                        location=default_location,  # Use default location if exists, else None
                        first_name=first_name,
                        last_name=last_name,
                        title=title,
                        email=email,
                        phone=phone,
                        is_active=True,
                        created_by=request.user
                    )
                    created_count += 1

                except Exception as e:
                    errors.append({
                        'row': row_num,
                        'error': str(e)
                    })

            response_data = {
                'created': created_count,
                'errors': errors
            }

            if errors:
                response_data['message'] = f'Imported {created_count} contacts with {len(errors)} errors'
            else:
                response_data['message'] = f'Successfully imported {created_count} contacts'

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': 'Error processing CSV file'},
                status=status.HTTP_400_BAD_REQUEST
            )


class DocumentationViewSet(SecureQuerySetMixin, OrganizationFilterMixin, VersionHistoryMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
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
        queryset = Documentation.objects.select_related('organization')
        return self.filter_by_organization_access(queryset)

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        # Create initial version on create
        self._create_version(instance, 'Initial version')

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        documentation = self.get_object()
        documentation.is_published = True
        documentation.save()
        return Response({'status': 'documentation published'})

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        documentation = self.get_object()
        documentation.is_published = False
        documentation.save()
        return Response({'status': 'documentation unpublished'})


class PasswordEntryViewSet(SecureQuerySetMixin, OrganizationFilterMixin, VersionHistoryMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
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
        queryset = PasswordEntry.objects.select_related('organization')
        return self.filter_by_organization_access(queryset)

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
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
            f"ip={request.META.get('REMOTE_ADDR', 'unknown')}"
        )

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


class ConfigurationViewSet(SecureQuerySetMixin, OrganizationFilterMixin, VersionHistoryMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
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
        queryset = Configuration.objects.select_related('organization')
        return self.filter_by_organization_access(queryset)

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        # Create initial version on create
        self._create_version(instance, 'Initial version')


class NetworkDeviceViewSet(SecureQuerySetMixin, OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for NetworkDevice CRUD operations."""
    serializer_class = NetworkDeviceSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['organization', 'device_type', 'location', 'is_active']
    search_fields = ['name', 'manufacturer', 'model', 'ip_address']
    ordering_fields = ['name', 'device_type', 'created_at']
    ordering = ['organization', 'device_type', 'name']

    def get_queryset(self):
        """Return only network devices from organizations the user has access to."""
        queryset = NetworkDevice.objects.select_related('organization', 'location')
        return self.filter_by_organization_access(queryset)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EndpointUserViewSet(SecureQuerySetMixin, OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for EndpointUser CRUD operations."""
    serializer_class = EndpointUserSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['organization', 'device_type', 'assigned_to', 'location', 'is_active']
    search_fields = ['name', 'manufacturer', 'model', 'hostname', 'ip_address']
    ordering_fields = ['name', 'device_type', 'created_at']
    ordering = ['organization', 'device_type', 'name']

    def get_queryset(self):
        """Return only endpoint users from organizations the user has access to."""
        queryset = EndpointUser.objects.select_related('organization', 'location', 'assigned_to')
        return self.filter_by_organization_access(queryset)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

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

    @action(detail=False, methods=['post'])
    def import_csv(self, request):
        """Import endpoint users from a CSV file."""
        # Security: File size limit (5MB max)
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
        MAX_ROWS = 10000

        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        csv_file = request.FILES['file']

        # Security: Check file size
        if csv_file.size > MAX_FILE_SIZE:
            return Response({'error': 'File size exceeds 5MB limit'}, status=status.HTTP_400_BAD_REQUEST)

        # Check file extension
        if not csv_file.name.endswith('.csv'):
            return Response({'error': 'File must be a CSV'}, status=status.HTTP_400_BAD_REQUEST)

        # Get organization_id from request
        org_id = request.data.get('organization_id')
        if not org_id:
            return Response({'error': 'organization_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify organization exists and user has access
        try:
            organization = Organization.objects.get(id=org_id)
            # Security: Check user has access to this organization
            if not OrganizationMember.user_has_access(request.user, organization) and not request.user.is_superuser:
                return Response({'error': 'You do not have access to this organization'}, status=status.HTTP_403_FORBIDDEN)
        except Organization.DoesNotExist:
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)

        # Valid device types
        valid_device_types = ['desktop', 'laptop', 'workstation', 'other']

        # Read and decode CSV file
        try:
            # Use utf-8-sig to handle BOM (Byte Order Mark) from Excel-exported CSV files
            decoded_file = csv_file.read().decode('utf-8-sig')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            created_count = 0
            errors = []

            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                # Security: Limit number of rows
                if row_num > MAX_ROWS + 1:
                    errors.append({'row': row_num, 'error': f'Exceeded maximum row limit of {MAX_ROWS}'})
                    break

                try:
                    # Security: Sanitize inputs - strip and limit length
                    name = row.get('name', '').strip()[:255]
                    device_type = row.get('device_type', 'desktop').strip().lower()[:50]
                    manufacturer = row.get('manufacturer', '').strip()[:255]
                    model = row.get('model', '').strip()[:255]
                    cpu = row.get('cpu', '').strip()[:255]
                    ram = row.get('ram', '').strip()[:100]
                    storage = row.get('storage', '').strip()[:255]
                    gpu = row.get('gpu', '').strip()[:255]
                    operating_system = row.get('operating_system', '').strip()[:255]
                    ip_address = row.get('ip_address', '').strip()[:50]
                    mac_address = row.get('mac_address', '').strip()[:50]
                    hostname = row.get('hostname', '').strip()[:255]
                    serial_number = row.get('serial_number', '').strip()[:255]

                    # Validate required field
                    if not name:
                        errors.append({'row': row_num, 'error': 'Name is required'})
                        continue

                    # Validate device_type
                    if device_type not in valid_device_types:
                        device_type = 'other'

                    # Create endpoint user
                    EndpointUser.objects.create(
                        organization=organization,
                        name=name,
                        device_type=device_type,
                        manufacturer=manufacturer,
                        model=model,
                        cpu=cpu,
                        ram=ram,
                        storage=storage,
                        gpu=gpu,
                        operating_system=operating_system,
                        ip_address=ip_address,
                        mac_address=mac_address,
                        hostname=hostname,
                        serial_number=serial_number,
                        is_active=True,
                        created_by=request.user
                    )
                    created_count += 1

                except Exception as e:
                    errors.append({'row': row_num, 'error': str(e)})

            response_data = {
                'created': created_count,
                'errors': errors
            }

            if errors:
                response_data['message'] = f'Imported {created_count} endpoint users with {len(errors)} errors'
            else:
                response_data['message'] = f'Successfully imported {created_count} endpoint users'

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': 'Error processing CSV file'}, status=status.HTTP_400_BAD_REQUEST)


class ServerViewSet(SecureQuerySetMixin, OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Server CRUD operations."""
    serializer_class = ServerSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['organization', 'server_type', 'location', 'is_active']
    search_fields = ['name', 'role', 'manufacturer', 'model', 'hostname', 'ip_address']
    ordering_fields = ['name', 'server_type', 'created_at']
    ordering = ['organization', 'server_type', 'name']

    def get_queryset(self):
        """Return only servers from organizations the user has access to."""
        queryset = Server.objects.select_related('organization', 'location')
        return self.filter_by_organization_access(queryset)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PeripheralViewSet(SecureQuerySetMixin, OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Peripheral CRUD operations."""
    serializer_class = PeripheralSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['organization', 'device_type', 'location', 'is_active']
    search_fields = ['name', 'manufacturer', 'model', 'ip_address']
    ordering_fields = ['name', 'device_type', 'created_at']
    ordering = ['organization', 'device_type', 'name']

    def get_queryset(self):
        """Return only peripherals from organizations the user has access to."""
        queryset = Peripheral.objects.select_related('organization', 'location')
        return self.filter_by_organization_access(queryset)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SoftwareViewSet(SecureQuerySetMixin, OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Software CRUD operations."""
    serializer_class = SoftwareSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['organization', 'software_type', 'license_type', 'is_active']
    search_fields = ['name', 'vendor', 'license_key']
    ordering_fields = ['name', 'software_type', 'expiry_date', 'created_at']
    ordering = ['organization', 'software_type', 'name']

    def get_queryset(self):
        """Return only software from organizations the user has access to."""
        queryset = Software.objects.select_related('organization').prefetch_related(
            'software_assignments__contact',
            'software_assignments__created_by'
        )
        return self.filter_by_organization_access(queryset)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class BackupViewSet(SecureQuerySetMixin, OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Backup CRUD operations."""
    serializer_class = BackupSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['organization', 'backup_type', 'backup_status', 'location', 'is_active']
    search_fields = ['name', 'vendor', 'target_systems', 'storage_location']
    ordering_fields = ['name', 'backup_type', 'last_backup_date', 'created_at']
    ordering = ['organization', 'backup_type', 'name']

    def get_queryset(self):
        """Return only backups from organizations the user has access to."""
        queryset = Backup.objects.select_related('organization', 'location')
        return self.filter_by_organization_access(queryset)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class VoIPViewSet(SecureQuerySetMixin, OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for VoIP CRUD operations."""
    serializer_class = VoIPSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['organization', 'voip_type', 'license_type', 'is_active']
    search_fields = ['name', 'vendor', 'license_key']
    ordering_fields = ['name', 'voip_type', 'expiry_date', 'created_at']
    ordering = ['organization', 'voip_type', 'name']

    def get_queryset(self):
        """Return only VoIP from organizations the user has access to."""
        queryset = VoIP.objects.select_related('organization').prefetch_related(
            'voip_assignments__contact',
            'voip_assignments__created_by'
        )
        return self.filter_by_organization_access(queryset)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
