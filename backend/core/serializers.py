from rest_framework import serializers
from .models import (
    Organization, Location, Contact, Documentation,
    PasswordEntry, Configuration, NetworkDevice, InternetConnection, EndpointUser, Server, Peripheral, Software, SoftwareAssignment, Backup, VoIP, VoIPAssignment,
    DocumentationVersion, PasswordEntryVersion, ConfigurationVersion
)
from users.serializers import UserSerializer
from .encryption import encrypt_password, decrypt_password, is_encrypted


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
    """
    Serializer for password entries with encryption.
    Passwords are encrypted at rest and never exposed in list/detail responses.
    Use the retrieve_password action to get the decrypted password.
    """
    # Password is write-only - never returned in API responses for security
    # Required on create, optional on update (blank/empty means keep existing)
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        style={'input_type': 'password'}
    )
    # Indicator that password exists (without exposing it)
    has_password = serializers.SerializerMethodField()

    class Meta(OrganizationOwnedSerializer.Meta):
        model = PasswordEntry
        fields = [
            'id', 'organization', 'organization_name', 'name', 'username',
            'password', 'has_password', 'url', 'notes', 'category', 'is_encrypted',
            'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_has_password(self, obj):
        """Indicate if a password is set without exposing it."""
        return bool(obj.password)

    def validate_password(self, value):
        """Validate password - required on create, optional on update."""
        # On create (no instance), password is required
        if self.instance is None and not value:
            raise serializers.ValidationError("Password is required when creating a new entry.")
        return value

    def create(self, validated_data):
        """Encrypt password before saving."""
        if 'password' in validated_data and validated_data['password']:
            validated_data['password'] = encrypt_password(validated_data['password'])
            validated_data['is_encrypted'] = True
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Encrypt password if being updated, otherwise keep existing."""
        # If password is not provided or is empty, keep the existing password
        if 'password' not in validated_data or not validated_data.get('password'):
            validated_data.pop('password', None)  # Remove from validated_data to keep existing
        else:
            # New password provided - encrypt it
            validated_data['password'] = encrypt_password(validated_data['password'])
            validated_data['is_encrypted'] = True
        return super().update(instance, validated_data)


class ConfigurationSerializer(OrganizationOwnedSerializer):
    class Meta(OrganizationOwnedSerializer.Meta):
        model = Configuration
        fields = [
            'id', 'organization', 'organization_name', 'name', 'config_type',
            'content', 'description', 'version', 'is_active', 'created_by',
            'created_at', 'updated_at', 'deleted_at', 'deleted_by'
        ]


class InternetConnectionSerializer(serializers.ModelSerializer):
    """Serializer for ISP/internet connections on network devices."""
    speed_display = serializers.CharField(read_only=True)

    class Meta:
        model = InternetConnection
        fields = [
            'id', 'provider_name', 'connection_type', 'download_speed', 'upload_speed',
            'speed_display', 'is_primary', 'account_number', 'notes', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'speed_display', 'created_at', 'updated_at']


class NetworkDeviceSerializer(LocationOwnedSerializer):
    internet_connections = InternetConnectionSerializer(many=True, required=False)

    class Meta(LocationOwnedSerializer.Meta):
        model = NetworkDevice
        fields = [
            'id', 'organization', 'organization_name', 'name', 'device_type',
            'internet_provider', 'internet_speed', 'internet_connections',
            'manufacturer', 'model', 'ip_address', 'mac_address', 'serial_number',
            'firmware_version', 'location', 'location_name', 'notes', 'is_active',
            'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by'
        ]

    def create(self, validated_data):
        connections_data = validated_data.pop('internet_connections', [])
        device = super().create(validated_data)
        for conn_data in connections_data:
            InternetConnection.objects.create(
                network_device=device,
                created_by=validated_data.get('created_by'),
                **conn_data
            )
        return device

    def update(self, instance, validated_data):
        connections_data = validated_data.pop('internet_connections', None)
        device = super().update(instance, validated_data)

        if connections_data is not None:
            # Clear existing connections and recreate
            instance.internet_connections.all().delete()
            for conn_data in connections_data:
                InternetConnection.objects.create(
                    network_device=device,
                    created_by=instance.created_by,
                    **conn_data
                )
        return device


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
    host_server_name = serializers.CharField(source='host_server.name', read_only=True, allow_null=True)

    class Meta(LocationOwnedSerializer.Meta):
        model = Server
        fields = [
            'id', 'organization', 'organization_name', 'name', 'server_type',
            'role', 'manufacturer', 'model', 'cpu', 'ram', 'storage',
            'storage_drives', 'raid_configuration', 'host_server', 'host_server_name',
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
    """
    Serializer for password entry versions.
    Includes decrypted password for version history viewing.
    """
    # Include decrypted password for version history
    password = serializers.SerializerMethodField()
    has_password = serializers.SerializerMethodField()

    class Meta(VersionSerializer.Meta):
        model = PasswordEntryVersion
        fields = [
            'id', 'password_entry', 'version_number', 'name', 'username',
            'password', 'has_password', 'url', 'notes', 'category', 'is_encrypted',
            'change_note', 'created_at', 'created_by'
        ]

    def get_password(self, obj):
        """Return decrypted password for version history viewing."""
        if obj.password and obj.is_encrypted:
            try:
                return decrypt_password(obj.password)
            except Exception:
                return '(decryption failed)'
        return obj.password or ''

    def get_has_password(self, obj):
        """Indicate if a password was set in this version."""
        return bool(obj.password)


class ConfigurationVersionSerializer(VersionSerializer):
    class Meta(VersionSerializer.Meta):
        model = ConfigurationVersion
        fields = [
            'id', 'configuration', 'version_number', 'name', 'config_type',
            'content', 'description', 'version', 'is_active', 'change_note',
            'created_at', 'created_by'
        ]


# =============================================================================
# Unified Entity Version Serializer (Single Source of Truth)
# =============================================================================

from .models import EntityVersion


class EntityVersionSerializer(serializers.ModelSerializer):
    """
    Serializer for the unified EntityVersion model.

    This is the Single Source of Truth for all entity version history,
    replacing the per-entity version serializers above.
    """
    created_by = UserSerializer(read_only=True)
    content_type_name = serializers.SerializerMethodField()

    class Meta:
        model = EntityVersion
        fields = [
            'id', 'content_type', 'content_type_name', 'object_id',
            'version_number', 'snapshot', 'change_note',
            'created_at', 'created_by'
        ]
        read_only_fields = ['id', 'content_type', 'object_id', 'version_number', 'created_at', 'created_by']

    def get_content_type_name(self, obj):
        """Get human-readable name of the versioned entity type."""
        return obj.content_type.model.replace('_', ' ').title()
