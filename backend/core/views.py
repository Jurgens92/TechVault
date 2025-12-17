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
    DocumentationVersion, PasswordEntryVersion, ConfigurationVersion
)
from .serializers import (
    OrganizationSerializer, LocationSerializer, ContactSerializer,
    DocumentationSerializer, PasswordEntrySerializer, ConfigurationSerializer,
    NetworkDeviceSerializer, EndpointUserSerializer, ServerSerializer, PeripheralSerializer, SoftwareSerializer, BackupSerializer, VoIPSerializer,
    DocumentationVersionSerializer, PasswordEntryVersionSerializer, ConfigurationVersionSerializer
)


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


class SoftDeleteViewSetMixin:
    """Mixin to add soft delete functionality to ViewSets."""

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

        # Apply organization filter if provided
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


class OrganizationViewSet(SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Organization CRUD operations."""
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active', 'country']
    search_fields = ['name', 'description', 'email']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        return Organization.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if query:
            organizations = Organization.objects.filter(
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


class LocationViewSet(OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Location CRUD operations."""
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['organization', 'is_active', 'country']
    search_fields = ['name', 'city', 'address']
    ordering_fields = ['name', 'city', 'created_at']
    ordering = ['organization', 'name']

    def get_queryset(self):
        return Location.objects.select_related('organization')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ContactViewSet(LocationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Contact CRUD operations."""
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['organization', 'location', 'is_active']
    search_fields = ['first_name', 'last_name', 'email', 'title']
    ordering_fields = ['last_name', 'first_name', 'created_at']
    ordering = ['organization', 'last_name', 'first_name']

    def get_queryset(self):
        return Contact.objects.select_related('organization', 'location')

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
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        csv_file = request.FILES['file']

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

        # Verify organization exists
        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response(
                {'error': 'Organization not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Read and decode CSV file
        try:
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            created_count = 0
            errors = []

            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                try:
                    # Create contact (is_active always set to True)
                    Contact.objects.create(
                        organization=organization,
                        first_name=row.get('first_name', '').strip(),
                        last_name=row.get('last_name', '').strip(),
                        title=row.get('title', '').strip(),
                        email=row.get('email', '').strip(),
                        phone=row.get('phone', '').strip(),
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
                {'error': f'Error processing CSV file: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class DocumentationViewSet(OrganizationFilterMixin, VersionHistoryMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Documentation CRUD operations."""
    serializer_class = DocumentationSerializer
    permission_classes = [IsAuthenticated]
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
        return Documentation.objects.select_related('organization')

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


class PasswordEntryViewSet(OrganizationFilterMixin, VersionHistoryMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for PasswordEntry CRUD operations."""
    serializer_class = PasswordEntrySerializer
    permission_classes = [IsAuthenticated]
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
        return PasswordEntry.objects.select_related('organization')

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        # Create initial version on create
        self._create_version(instance, 'Initial version')


class ConfigurationViewSet(OrganizationFilterMixin, VersionHistoryMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Configuration CRUD operations."""
    serializer_class = ConfigurationSerializer
    permission_classes = [IsAuthenticated]
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
        return Configuration.objects.select_related('organization')

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        # Create initial version on create
        self._create_version(instance, 'Initial version')


class NetworkDeviceViewSet(OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for NetworkDevice CRUD operations."""
    serializer_class = NetworkDeviceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['organization', 'device_type', 'location', 'is_active']
    search_fields = ['name', 'manufacturer', 'model', 'ip_address']
    ordering_fields = ['name', 'device_type', 'created_at']
    ordering = ['organization', 'device_type', 'name']

    def get_queryset(self):
        return NetworkDevice.objects.select_related('organization', 'location')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EndpointUserViewSet(OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for EndpointUser CRUD operations."""
    serializer_class = EndpointUserSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['organization', 'device_type', 'assigned_to', 'location', 'is_active']
    search_fields = ['name', 'manufacturer', 'model', 'hostname', 'ip_address']
    ordering_fields = ['name', 'device_type', 'created_at']
    ordering = ['organization', 'device_type', 'name']

    def get_queryset(self):
        return EndpointUser.objects.select_related('organization', 'location', 'assigned_to')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ServerViewSet(OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Server CRUD operations."""
    serializer_class = ServerSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['organization', 'server_type', 'location', 'is_active']
    search_fields = ['name', 'role', 'manufacturer', 'model', 'hostname', 'ip_address']
    ordering_fields = ['name', 'server_type', 'created_at']
    ordering = ['organization', 'server_type', 'name']

    def get_queryset(self):
        return Server.objects.select_related('organization', 'location')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PeripheralViewSet(OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Peripheral CRUD operations."""
    serializer_class = PeripheralSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['organization', 'device_type', 'location', 'is_active']
    search_fields = ['name', 'manufacturer', 'model', 'ip_address']
    ordering_fields = ['name', 'device_type', 'created_at']
    ordering = ['organization', 'device_type', 'name']

    def get_queryset(self):
        return Peripheral.objects.select_related('organization', 'location')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SoftwareViewSet(OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Software CRUD operations."""
    serializer_class = SoftwareSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['organization', 'software_type', 'license_type', 'is_active']
    search_fields = ['name', 'vendor', 'license_key']
    ordering_fields = ['name', 'software_type', 'expiry_date', 'created_at']
    ordering = ['organization', 'software_type', 'name']

    def get_queryset(self):
        return Software.objects.select_related('organization').prefetch_related(
            'software_assignments__contact',
            'software_assignments__created_by'
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class BackupViewSet(OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Backup CRUD operations."""
    serializer_class = BackupSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['organization', 'backup_type', 'backup_status', 'location', 'is_active']
    search_fields = ['name', 'vendor', 'target_systems', 'storage_location']
    ordering_fields = ['name', 'backup_type', 'last_backup_date', 'created_at']
    ordering = ['organization', 'backup_type', 'name']

    def get_queryset(self):
        return Backup.objects.select_related('organization', 'location')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class VoIPViewSet(OrganizationFilterMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for VoIP CRUD operations."""
    serializer_class = VoIPSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['organization', 'voip_type', 'license_type', 'is_active']
    search_fields = ['name', 'vendor', 'license_key']
    ordering_fields = ['name', 'voip_type', 'expiry_date', 'created_at']
    ordering = ['organization', 'voip_type', 'name']

    def get_queryset(self):
        return VoIP.objects.select_related('organization').prefetch_related(
            'voip_assignments__contact',
            'voip_assignments__created_by'
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
