from rest_framework import serializers
from .models import (
    Organization, Location, Contact, Documentation,
    PasswordEntry, Configuration, NetworkDevice, EndpointUser, Server, Peripheral, Software, SoftwareAssignment, Backup, VoIP, VoIPAssignment
)
from users.serializers import UserSerializer


class OrganizationSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    deleted_by = UserSerializer(read_only=True)

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'description', 'website', 'phone', 'email',
            'address', 'city', 'state_province', 'postal_code', 'country',
            'is_active', 'created_by', 'created_at', 'updated_at',
            'deleted_at', 'deleted_by'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by']


class LocationSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    created_by = UserSerializer(read_only=True)
    deleted_by = UserSerializer(read_only=True)

    class Meta:
        model = Location
        fields = [
            'id', 'organization', 'organization_name', 'name', 'description',
            'address', 'city', 'state_province', 'postal_code', 'country',
            'phone', 'is_active', 'created_by', 'created_at', 'updated_at',
            'deleted_at', 'deleted_by'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by']


class ContactSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True, allow_null=True)
    full_name = serializers.CharField(read_only=True)
    created_by = UserSerializer(read_only=True)
    deleted_by = UserSerializer(read_only=True)

    class Meta:
        model = Contact
        fields = [
            'id', 'organization', 'organization_name', 'location', 'location_name',
            'first_name', 'last_name', 'full_name', 'title', 'email', 'phone',
            'mobile', 'notes', 'is_active', 'created_by', 'created_at', 'updated_at',
            'deleted_at', 'deleted_by'
        ]
        read_only_fields = ['id', 'full_name', 'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by']


class DocumentationSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    created_by = UserSerializer(read_only=True)
    deleted_by = UserSerializer(read_only=True)

    class Meta:
        model = Documentation
        fields = [
            'id', 'organization', 'organization_name', 'title', 'content',
            'category', 'tags', 'is_published', 'version', 'created_by',
            'created_at', 'updated_at', 'deleted_at', 'deleted_by'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by']


class PasswordEntrySerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    created_by = UserSerializer(read_only=True)
    deleted_by = UserSerializer(read_only=True)

    class Meta:
        model = PasswordEntry
        fields = [
            'id', 'organization', 'organization_name', 'name', 'username',
            'password', 'url', 'notes', 'category', 'is_encrypted',
            'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by']


class ConfigurationSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    created_by = UserSerializer(read_only=True)
    deleted_by = UserSerializer(read_only=True)

    class Meta:
        model = Configuration
        fields = [
            'id', 'organization', 'organization_name', 'name', 'config_type',
            'content', 'description', 'version', 'is_active', 'created_by',
            'created_at', 'updated_at', 'deleted_at', 'deleted_by'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by']


class NetworkDeviceSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True, allow_null=True)
    created_by = UserSerializer(read_only=True)
    deleted_by = UserSerializer(read_only=True)

    class Meta:
        model = NetworkDevice
        fields = [
            'id', 'organization', 'organization_name', 'name', 'device_type',
            'internet_provider', 'internet_speed', 'manufacturer', 'model',
            'ip_address', 'mac_address', 'serial_number', 'firmware_version',
            'location', 'location_name', 'notes', 'is_active', 'created_by',
            'created_at', 'updated_at', 'deleted_at', 'deleted_by'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by']


class EndpointUserSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True, allow_null=True)
    assigned_to_name = serializers.CharField(source='assigned_to.full_name', read_only=True, allow_null=True)
    created_by = UserSerializer(read_only=True)
    deleted_by = UserSerializer(read_only=True)

    class Meta:
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
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by']


class ServerSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True, allow_null=True)
    created_by = UserSerializer(read_only=True)
    deleted_by = UserSerializer(read_only=True)

    class Meta:
        model = Server
        fields = [
            'id', 'organization', 'organization_name', 'name', 'server_type',
            'role', 'manufacturer', 'model', 'cpu', 'ram', 'storage',
            'operating_system', 'software_installed', 'ip_address', 'mac_address',
            'hostname', 'serial_number', 'location', 'location_name', 'notes',
            'is_active', 'created_by', 'created_at', 'updated_at',
            'deleted_at', 'deleted_by'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by']


class PeripheralSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True, allow_null=True)
    created_by = UserSerializer(read_only=True)
    deleted_by = UserSerializer(read_only=True)

    class Meta:
        model = Peripheral
        fields = [
            'id', 'organization', 'organization_name', 'name', 'device_type',
            'manufacturer', 'model', 'ip_address', 'mac_address', 'serial_number',
            'location', 'location_name', 'notes', 'is_active', 'created_by',
            'created_at', 'updated_at', 'deleted_at', 'deleted_by'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by']


class SoftwareAssignmentSerializer(serializers.ModelSerializer):
    contact_id = serializers.PrimaryKeyRelatedField(source='contact', queryset=Contact.objects.all())
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    contact_email = serializers.CharField(source='contact.email', read_only=True)
    created_by = UserSerializer(read_only=True)
    deleted_by = UserSerializer(read_only=True)

    class Meta:
        model = SoftwareAssignment
        fields = [
            'id', 'contact_id', 'contact_name', 'contact_email', 'created_at',
            'created_by', 'updated_at', 'deleted_at', 'deleted_by'
        ]
        read_only_fields = ['id', 'contact_name', 'contact_email', 'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by']


class SoftwareSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    assigned_contacts = SoftwareAssignmentSerializer(source='software_assignments', many=True, read_only=True)
    assigned_contact_ids = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    assigned_count = serializers.IntegerField(read_only=True)
    available_licenses = serializers.IntegerField(read_only=True)
    created_by = UserSerializer(read_only=True)
    deleted_by = UserSerializer(read_only=True)

    class Meta:
        model = Software
        fields = [
            'id', 'organization', 'organization_name', 'name', 'software_type',
            'assigned_contact_ids', 'assigned_contacts', 'license_key', 'version', 'license_type',
            'purchase_date', 'expiry_date', 'vendor', 'quantity', 'notes',
            'assigned_count', 'available_licenses', 'is_active', 'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by']

    def create(self, validated_data):
        contact_ids = validated_data.pop('assigned_contact_ids', [])
        software = Software.objects.create(**validated_data)

        # Get the user from the request context
        request = self.context.get('request')
        user = request.user if request else None

        for contact in contact_ids:
            SoftwareAssignment.objects.create(
                software=software,
                contact=contact,
                created_by=user
            )

        return software

    def update(self, instance, validated_data):
        contact_ids = validated_data.pop('assigned_contact_ids', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if contact_ids is not None:
            # Get the user from the request context
            request = self.context.get('request')
            user = request.user if request else None

            # Clear existing assignments and create new ones
            instance.software_assignments.all().delete()
            for contact in contact_ids:
                SoftwareAssignment.objects.create(
                    software=instance,
                    contact=contact,
                    created_by=user
                )

        return instance


class BackupSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True, allow_null=True)
    created_by = UserSerializer(read_only=True)
    deleted_by = UserSerializer(read_only=True)

    class Meta:
        model = Backup
        fields = [
            'id', 'organization', 'organization_name', 'name', 'backup_type',
            'vendor', 'frequency', 'retention_period', 'storage_location', 'storage_capacity',
            'target_systems', 'last_backup_date', 'next_backup_date', 'backup_status',
            'location', 'location_name', 'notes', 'is_active',
            'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by']


class VoIPAssignmentSerializer(serializers.ModelSerializer):
    contact_id = serializers.PrimaryKeyRelatedField(source='contact', queryset=Contact.objects.all())
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    contact_email = serializers.CharField(source='contact.email', read_only=True)
    created_by = UserSerializer(read_only=True)
    deleted_by = UserSerializer(read_only=True)

    class Meta:
        model = VoIPAssignment
        fields = [
            'id', 'contact_id', 'contact_name', 'contact_email', 'extension', 'phone_number',
            'created_at', 'created_by', 'updated_at', 'deleted_at', 'deleted_by'
        ]
        read_only_fields = ['id', 'contact_name', 'contact_email', 'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by']


class VoIPSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    assigned_contacts = VoIPAssignmentSerializer(source='voip_assignments', many=True, read_only=True)
    assigned_contact_ids = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    assigned_count = serializers.IntegerField(read_only=True)
    available_licenses = serializers.IntegerField(read_only=True)
    created_by = UserSerializer(read_only=True)
    deleted_by = UserSerializer(read_only=True)

    class Meta:
        model = VoIP
        fields = [
            'id', 'organization', 'organization_name', 'name', 'voip_type',
            'assigned_contact_ids', 'assigned_contacts', 'license_key', 'version', 'license_type',
            'purchase_date', 'expiry_date', 'vendor', 'quantity', 'phone_numbers',
            'extensions', 'notes', 'assigned_count', 'available_licenses', 'is_active',
            'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'deleted_at', 'deleted_by']

    def create(self, validated_data):
        contact_ids = validated_data.pop('assigned_contact_ids', [])
        voip = VoIP.objects.create(**validated_data)

        # Get the user from the request context
        request = self.context.get('request')
        user = request.user if request else None

        for contact in contact_ids:
            VoIPAssignment.objects.create(
                voip=voip,
                contact=contact,
                created_by=user
            )

        return voip

    def update(self, instance, validated_data):
        contact_ids = validated_data.pop('assigned_contact_ids', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if contact_ids is not None:
            # Get the user from the request context
            request = self.context.get('request')
            user = request.user if request else None

            # Clear existing assignments and create new ones
            instance.voip_assignments.all().delete()
            for contact in contact_ids:
                VoIPAssignment.objects.create(
                    voip=instance,
                    contact=contact,
                    created_by=user
                )

        return instance
