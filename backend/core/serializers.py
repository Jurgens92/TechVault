from rest_framework import serializers
from .models import (
    Organization, Location, Contact, Documentation,
    PasswordEntry, Configuration, NetworkDevice, EndpointUser, Server, Peripheral, Software, SoftwareAssignment, Backup, VoIP, VoIPAssignment,
    DocumentationVersion, PasswordEntryVersion, ConfigurationVersion
)
from users.serializers import UserSerializer


# Base serializer classes to reduce duplication

class BaseAuditedSerializer(serializers.ModelSerializer):
    """Base serializer with common audit fields (created_by, deleted_by)."""
    created_by = UserSerializer(read_only=True)
    deleted_by = UserSerializer(read_only=True)

    class Meta:
        abstract = True
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by']


class OrganizationOwnedSerializer(BaseAuditedSerializer):
    """Base serializer for models that belong to an organization."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta(BaseAuditedSerializer.Meta):
        abstract = True


class LocationOwnedSerializer(OrganizationOwnedSerializer):
    """Base serializer for models that have both organization and location."""
    location_name = serializers.CharField(source='location.name', read_only=True, allow_null=True)

    class Meta(OrganizationOwnedSerializer.Meta):
        abstract = True


class OrganizationSerializer(BaseAuditedSerializer):
    class Meta(BaseAuditedSerializer.Meta):
        model = Organization
        fields = [
            'id', 'name', 'description', 'website', 'phone', 'email',
            'address', 'city', 'state_province', 'postal_code', 'country',
            'is_active', 'created_by', 'created_at', 'updated_at',
            'deleted_at', 'deleted_by'
        ]


class LocationSerializer(OrganizationOwnedSerializer):
    class Meta(OrganizationOwnedSerializer.Meta):
        model = Location
        fields = [
            'id', 'organization', 'organization_name', 'name', 'description',
            'address', 'city', 'state_province', 'postal_code', 'country',
            'phone', 'is_active', 'created_by', 'created_at', 'updated_at',
            'deleted_at', 'deleted_by'
        ]


class ContactSerializer(LocationOwnedSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta(LocationOwnedSerializer.Meta):
        model = Contact
        fields = [
            'id', 'organization', 'organization_name', 'location', 'location_name',
            'first_name', 'last_name', 'full_name', 'title', 'email', 'phone',
            'mobile', 'notes', 'is_active', 'created_by', 'created_at', 'updated_at',
            'deleted_at', 'deleted_by'
        ]
        read_only_fields = ['id', 'full_name', 'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by']


class DocumentationSerializer(OrganizationOwnedSerializer):
    class Meta(OrganizationOwnedSerializer.Meta):
        model = Documentation
        fields = [
            'id', 'organization', 'organization_name', 'title', 'content',
            'category', 'tags', 'is_published', 'version', 'created_by',
            'created_at', 'updated_at', 'deleted_at', 'deleted_by'
        ]


class PasswordEntrySerializer(OrganizationOwnedSerializer):
    class Meta(OrganizationOwnedSerializer.Meta):
        model = PasswordEntry
        fields = [
            'id', 'organization', 'organization_name', 'name', 'username',
            'password', 'url', 'notes', 'category', 'is_encrypted',
            'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by'
        ]


class ConfigurationSerializer(OrganizationOwnedSerializer):
    class Meta(OrganizationOwnedSerializer.Meta):
        model = Configuration
        fields = [
            'id', 'organization', 'organization_name', 'name', 'config_type',
            'content', 'description', 'version', 'is_active', 'created_by',
            'created_at', 'updated_at', 'deleted_at', 'deleted_by'
        ]


class NetworkDeviceSerializer(LocationOwnedSerializer):
    class Meta(LocationOwnedSerializer.Meta):
        model = NetworkDevice
        fields = [
            'id', 'organization', 'organization_name', 'name', 'device_type',
            'internet_provider', 'internet_speed', 'manufacturer', 'model',
            'ip_address', 'mac_address', 'serial_number', 'firmware_version',
            'location', 'location_name', 'notes', 'is_active', 'created_by',
            'created_at', 'updated_at', 'deleted_at', 'deleted_by'
        ]


class EndpointUserSerializer(LocationOwnedSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.full_name', read_only=True, allow_null=True)

    class Meta(LocationOwnedSerializer.Meta):
        model = EndpointUser
        fields = [
            'id', 'organization', 'organization_name', 'name', 'device_type',
            'assigned_to', 'assigned_to_name', 'manufacturer', 'model', 'cpu',
            'ram', 'storage', 'gpu', 'operating_system', 'software_installed',
            'ip_address', 'mac_address', 'hostname', 'serial_number',
            'purchase_date', 'warranty_expiry', 'location', 'location_name',
            'notes', 'is_active', 'created_by', 'created_at', 'updated_at',
            'deleted_at', 'deleted_by'
        ]


class ServerSerializer(LocationOwnedSerializer):
    class Meta(LocationOwnedSerializer.Meta):
        model = Server
        fields = [
            'id', 'organization', 'organization_name', 'name', 'server_type',
            'role', 'manufacturer', 'model', 'cpu', 'ram', 'storage',
            'operating_system', 'software_installed', 'ip_address', 'mac_address',
            'hostname', 'serial_number', 'location', 'location_name', 'notes',
            'is_active', 'created_by', 'created_at', 'updated_at',
            'deleted_at', 'deleted_by'
        ]


class PeripheralSerializer(LocationOwnedSerializer):
    class Meta(LocationOwnedSerializer.Meta):
        model = Peripheral
        fields = [
            'id', 'organization', 'organization_name', 'name', 'device_type',
            'manufacturer', 'model', 'ip_address', 'mac_address', 'serial_number',
            'location', 'location_name', 'notes', 'is_active', 'created_by',
            'created_at', 'updated_at', 'deleted_at', 'deleted_by'
        ]


class SoftwareAssignmentSerializer(BaseAuditedSerializer):
    contact_id = serializers.PrimaryKeyRelatedField(source='contact', queryset=Contact.objects.all())
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    contact_email = serializers.CharField(source='contact.email', read_only=True)

    class Meta(BaseAuditedSerializer.Meta):
        model = SoftwareAssignment
        fields = [
            'id', 'contact_id', 'contact_name', 'contact_email', 'created_at',
            'created_by', 'updated_at', 'deleted_at', 'deleted_by'
        ]
        read_only_fields = ['id', 'contact_name', 'contact_email', 'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by']


class AssignableSerializer(OrganizationOwnedSerializer):
    """Base serializer for models with contact assignments (Software, VoIP)."""
    assigned_contact_ids = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    assigned_count = serializers.IntegerField(read_only=True)
    available_licenses = serializers.IntegerField(read_only=True)

    # Subclasses must define these
    assignment_model = None
    assignment_field_name = None  # e.g., 'software' or 'voip'
    assignments_related_name = None  # e.g., 'software_assignments' or 'voip_assignments'

    class Meta(OrganizationOwnedSerializer.Meta):
        abstract = True

    def _get_user(self):
        request = self.context.get('request')
        return request.user if request else None

    def create(self, validated_data):
        contact_ids = validated_data.pop('assigned_contact_ids', [])
        instance = self.Meta.model.objects.create(**validated_data)
        user = self._get_user()

        for contact in contact_ids:
            self.assignment_model.objects.create(
                **{self.assignment_field_name: instance},
                contact=contact,
                created_by=user
            )
        return instance

    def update(self, instance, validated_data):
        contact_ids = validated_data.pop('assigned_contact_ids', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if contact_ids is not None:
            user = self._get_user()
            getattr(instance, self.assignments_related_name).all().delete()
            for contact in contact_ids:
                self.assignment_model.objects.create(
                    **{self.assignment_field_name: instance},
                    contact=contact,
                    created_by=user
                )
        return instance


class SoftwareSerializer(AssignableSerializer):
    assigned_contacts = SoftwareAssignmentSerializer(source='software_assignments', many=True, read_only=True)

    assignment_model = SoftwareAssignment
    assignment_field_name = 'software'
    assignments_related_name = 'software_assignments'

    class Meta(AssignableSerializer.Meta):
        model = Software
        fields = [
            'id', 'organization', 'organization_name', 'name', 'software_type',
            'assigned_contact_ids', 'assigned_contacts', 'license_key', 'version', 'license_type',
            'purchase_date', 'expiry_date', 'vendor', 'quantity', 'notes',
            'assigned_count', 'available_licenses', 'is_active', 'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by'
        ]


class BackupSerializer(LocationOwnedSerializer):
    class Meta(LocationOwnedSerializer.Meta):
        model = Backup
        fields = [
            'id', 'organization', 'organization_name', 'name', 'backup_type',
            'vendor', 'frequency', 'retention_period', 'storage_location', 'storage_capacity',
            'target_systems', 'last_backup_date', 'next_backup_date', 'backup_status',
            'location', 'location_name', 'notes', 'is_active',
            'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by'
        ]


class VoIPAssignmentSerializer(BaseAuditedSerializer):
    contact_id = serializers.PrimaryKeyRelatedField(source='contact', queryset=Contact.objects.all())
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    contact_email = serializers.CharField(source='contact.email', read_only=True)

    class Meta(BaseAuditedSerializer.Meta):
        model = VoIPAssignment
        fields = [
            'id', 'contact_id', 'contact_name', 'contact_email', 'extension', 'phone_number',
            'created_at', 'created_by', 'updated_at', 'deleted_at', 'deleted_by'
        ]
        read_only_fields = ['id', 'contact_name', 'contact_email', 'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by']


class VoIPSerializer(AssignableSerializer):
    assigned_contacts = VoIPAssignmentSerializer(source='voip_assignments', many=True, read_only=True)

    assignment_model = VoIPAssignment
    assignment_field_name = 'voip'
    assignments_related_name = 'voip_assignments'

    class Meta(AssignableSerializer.Meta):
        model = VoIP
        fields = [
            'id', 'organization', 'organization_name', 'name', 'voip_type',
            'assigned_contact_ids', 'assigned_contacts', 'license_key', 'version', 'license_type',
            'purchase_date', 'expiry_date', 'vendor', 'quantity', 'phone_numbers',
            'extensions', 'notes', 'assigned_count', 'available_licenses', 'is_active',
            'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by'
        ]


# Version History Serializers

class VersionSerializer(serializers.ModelSerializer):
    """Base serializer for version history models."""
    created_by = UserSerializer(read_only=True)

    class Meta:
        abstract = True
        read_only_fields = ['id', 'created_at', 'created_by']


class DocumentationVersionSerializer(VersionSerializer):
    class Meta(VersionSerializer.Meta):
        model = DocumentationVersion
        fields = [
            'id', 'documentation', 'version_number', 'title', 'content',
            'category', 'tags', 'is_published', 'change_note',
            'created_at', 'created_by'
        ]


class PasswordEntryVersionSerializer(VersionSerializer):
    class Meta(VersionSerializer.Meta):
        model = PasswordEntryVersion
        fields = [
            'id', 'password_entry', 'version_number', 'name', 'username',
            'password', 'url', 'notes', 'category', 'is_encrypted',
            'change_note', 'created_at', 'created_by'
        ]


class ConfigurationVersionSerializer(VersionSerializer):
    class Meta(VersionSerializer.Meta):
        model = ConfigurationVersion
        fields = [
            'id', 'configuration', 'version_number', 'name', 'config_type',
            'content', 'description', 'version', 'is_active', 'change_note',
            'created_at', 'created_by'
        ]
