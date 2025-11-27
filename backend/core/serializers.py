from rest_framework import serializers
from .models import (
    Organization, Location, Contact, Documentation,
    PasswordEntry, Configuration, NetworkDevice, EndpointUser, Server, Peripheral
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
