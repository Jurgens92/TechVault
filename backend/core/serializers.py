from django.db import transaction
from rest_framework import serializers
from .models import (
    Organization, Location, Contact, Documentation,
    PasswordEntry, Configuration, NetworkDevice, InternetConnection, EndpointUser, Server, Peripheral, Software, SoftwareAssignment, Backup, VoIP, VoIPAssignment,
    DocumentationVersion, PasswordEntryVersion, ConfigurationVersion,
    AuditLog
)
from users.serializers import UserSerializer
from .encryption import encrypt_password, decrypt_password, is_encrypted


# Base serializer classes to reduce duplication

class BaseAuditedSerializer(serializers.ModelSerializer):
    """
    Base serializer with common audit fields (created_by, deleted_by) and shared
    integrity validation:

    - unique_active_fields: field combinations that must be unique among live
      (non soft-deleted) records. Returns a 400 instead of a database error.
    - same_organization_fields: related objects that must belong to the same
      organization as the record itself.
    """
    created_by = UserSerializer(read_only=True)
    deleted_by = UserSerializer(read_only=True)

    unique_active_fields = ()        # e.g. (('organization', 'name'),)
    unique_active_message = 'An item with this {field} already exists.'
    same_organization_fields = ()    # e.g. ('location', 'assigned_to')

    class Meta:
        abstract = True
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by']

    def get_unique_together_validators(self):
        """
        Uniqueness is enforced by validate() below (see unique_active_fields), which
        understands soft-deleted rows. DRF's auto-generated validators for the
        conditional database constraints are therefore not used: they would need
        the read-only deleted_at field, which is never part of the submitted data.
        """
        return []

    def _current(self, attrs, name):
        """Value of a field after this request: submitted value, else the stored one."""
        if name in attrs:
            return attrs[name]
        return getattr(self.instance, name, None) if self.instance is not None else None

    def validate(self, attrs):
        attrs = super().validate(attrs)
        model = self.Meta.model

        for combo in self.unique_active_fields:
            if self.instance is not None and not any(f in attrs for f in combo):
                continue  # none of these fields are changing
            lookup = {}
            for f in combo:
                value = self._current(attrs, f)
                lookup[f'{f}__iexact' if isinstance(value, str) else f] = value
            queryset = model.objects.filter(**lookup)
            if self.instance is not None:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                field = combo[-1]
                raise serializers.ValidationError({
                    field: self.unique_active_message.format(field=field.replace('_', ' '))
                })

        organization = self._current(attrs, 'organization')
        if organization is not None:
            for f in self.same_organization_fields:
                related = self._current(attrs, f)
                if related is not None and related.organization_id != organization.pk:
                    raise serializers.ValidationError({
                        f: 'Must belong to the same organization.'
                    })
        return attrs


class OrganizationOwnedSerializer(BaseAuditedSerializer):
    """Base serializer for models that belong to an organization."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta(BaseAuditedSerializer.Meta):
        abstract = True


class LocationOwnedSerializer(OrganizationOwnedSerializer):
    """Base serializer for models that have both organization and location."""
    location_name = serializers.CharField(source='location.name', read_only=True, allow_null=True)

    same_organization_fields = ('location',)

    class Meta(OrganizationOwnedSerializer.Meta):
        abstract = True


class OrganizationSerializer(BaseAuditedSerializer):
    unique_active_fields = (('name',),)
    unique_active_message = 'An organization with this name already exists.'

    class Meta(BaseAuditedSerializer.Meta):
        model = Organization
        fields = [
            'id', 'name', 'description', 'website', 'phone', 'email',
            'address', 'city', 'state_province', 'postal_code', 'country',
            'is_active', 'created_by', 'created_at', 'updated_at',
            'deleted_at', 'deleted_by'
        ]


class LocationSerializer(OrganizationOwnedSerializer):
    unique_active_fields = (('organization', 'name'),)
    unique_active_message = 'A location with this name already exists in this organization.'

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

    unique_active_fields = (('organization', 'email'),)
    unique_active_message = 'A contact with this email already exists in this organization.'

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
        read_only_fields = OrganizationOwnedSerializer.Meta.read_only_fields + ['is_encrypted']
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
            # force=True: user input is always plaintext, whatever it looks like
            validated_data['password'] = encrypt_password(validated_data['password'], force=True)
            validated_data['is_encrypted'] = True
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Encrypt password if being updated, otherwise keep existing."""
        # If password is not provided or is empty, keep the existing password
        if 'password' not in validated_data or not validated_data.get('password'):
            validated_data.pop('password', None)  # Remove from validated_data to keep existing
        else:
            # New password provided - encrypt it
            validated_data['password'] = encrypt_password(validated_data['password'], force=True)
            validated_data['is_encrypted'] = True
        return super().update(instance, validated_data)


class ConfigurationSerializer(OrganizationOwnedSerializer):
    unique_active_fields = (('organization', 'name'),)
    unique_active_message = 'A configuration with this name already exists in this organization.'

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

    @transaction.atomic
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

    @transaction.atomic
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

    same_organization_fields = ('location', 'assigned_to')

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

    same_organization_fields = ('location', 'host_server')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        host = attrs.get('host_server')
        if host is not None and self.instance is not None:
            # Walk up the host chain: a server cannot host itself, directly or indirectly
            seen = set()
            current = host
            while current is not None and current.pk not in seen:
                if current.pk == self.instance.pk:
                    raise serializers.ValidationError({
                        'host_server': 'A server cannot be its own host.'
                    })
                seen.add(current.pk)
                current = current.host_server
        return attrs

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

    def get_assigned_contacts(self, obj):
        """Assignments, excluding contacts that have been soft-deleted."""
        return self.assignment_serializer(obj.active_assignments, many=True).data

    def validate(self, data):
        """Check license quantity and that assigned contacts belong to the organization."""
        data = super().validate(data)
        contacts = data.get('assigned_contact_ids')

        quantity = data.get('quantity')
        if quantity is None and self.instance:
            quantity = self.instance.quantity
        if quantity is None:
            quantity = 1

        if contacts is not None:
            if len(set(c.pk for c in contacts)) != len(contacts):
                raise serializers.ValidationError({
                    'assigned_contact_ids': 'The same user cannot be assigned more than once.'
                })
            organization = self._current(data, 'organization')
            if organization is not None and any(c.organization_id != organization.pk for c in contacts):
                raise serializers.ValidationError({
                    'assigned_contact_ids': 'Assigned users must belong to the same organization.'
                })
            assigned = len(contacts)
        else:
            assigned = self.instance.assigned_count if self.instance else 0

        if assigned > quantity:
            raise serializers.ValidationError({
                'assigned_contact_ids' if contacts is not None else 'quantity': (
                    f'Cannot assign {assigned} users. '
                    f'Only {quantity} license(s) available.'
                )
            })
        return data

    def _sync_assignments(self, instance, contacts):
        """
        Bring assignments in line with the given contacts without recreating the
        ones that are unchanged (so per-assignment details such as a VoIP
        extension or phone number are preserved).
        """
        existing = {
            a.contact_id: a
            for a in self.assignment_model.all_objects.filter(**{self.assignment_field_name: instance})
        }
        wanted = {c.pk: c for c in contacts}
        user = self._get_user()

        for contact_id, assignment in existing.items():
            if contact_id not in wanted:
                assignment.hard_delete()
        for contact_id, contact in wanted.items():
            if contact_id not in existing:
                self.assignment_model.objects.create(
                    **{self.assignment_field_name: instance},
                    contact=contact,
                    created_by=user
                )
        # Drop any stale prefetch so the response reflects the new assignments
        if hasattr(instance, '_prefetched_objects_cache'):
            instance._prefetched_objects_cache.pop(self.assignments_related_name, None)

    @transaction.atomic
    def create(self, validated_data):
        contacts = validated_data.pop('assigned_contact_ids', [])
        instance = self.Meta.model.objects.create(**validated_data)
        self._sync_assignments(instance, contacts)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        contacts = validated_data.pop('assigned_contact_ids', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if contacts is not None:
            self._sync_assignments(instance, contacts)
        return instance


class SoftwareSerializer(AssignableSerializer):
    assigned_contacts = serializers.SerializerMethodField()
    assignment_serializer = SoftwareAssignmentSerializer

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
    assigned_contacts = serializers.SerializerMethodField()
    assignment_serializer = VoIPAssignmentSerializer

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
    Passwords are never exposed in version history responses for security.
    Use the retrieve_password action on the main PasswordEntry endpoint instead.
    """
    has_password = serializers.SerializerMethodField()

    class Meta(VersionSerializer.Meta):
        model = PasswordEntryVersion
        fields = [
            'id', 'password_entry', 'version_number', 'name', 'username',
            'has_password', 'url', 'notes', 'category', 'is_encrypted',
            'change_note', 'created_at', 'created_by'
        ]

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


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True, default='')
    user_name = serializers.CharField(source='user.full_name', read_only=True, default='System')

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_email', 'user_name', 'action',
            'entity_type', 'entity_id', 'entity_name',
            'organization_name', 'details', 'changes', 'ip_address', 'timestamp',
        ]
        read_only_fields = fields
