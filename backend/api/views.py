from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import (
    Organization, Location, Contact, Documentation,
    PasswordEntry, Configuration, NetworkDevice, EndpointUser, Server, Peripheral, Software, Backup
)
from core.serializers import (
    NetworkDeviceSerializer, EndpointUserSerializer, ServerSerializer, PeripheralSerializer, SoftwareSerializer, BackupSerializer
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def health_check(request):
    """
    Simple health check endpoint to verify authentication.
    """
    return Response({
        'status': 'ok',
        'user': request.user.email,
        'message': 'TechVault API is running'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics for all entities.
    """
    return Response({
        'organizations': Organization.objects.count(),
        'locations': Location.objects.count(),
        'contacts': Contact.objects.count(),
        'documentations': Documentation.objects.count(),
        'passwords': PasswordEntry.objects.count(),
        'configurations': Configuration.objects.count(),
        'network_devices': NetworkDevice.objects.count(),
        'endpoint_users': EndpointUser.objects.count(),
        'servers': Server.objects.count(),
        'peripherals': Peripheral.objects.count(),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def diagram_data(request):
    """
    Get all endpoint data for diagram generation.
    """
    org_id = request.query_params.get('organization_id')

    # Filter by organization if provided
    if org_id:
        network_devices = NetworkDevice.objects.filter(organization_id=org_id, is_active=True)
        endpoint_users = EndpointUser.objects.filter(organization_id=org_id, is_active=True)
        servers = Server.objects.filter(organization_id=org_id, is_active=True)
        peripherals = Peripheral.objects.filter(organization_id=org_id, is_active=True)
        backups = Backup.objects.filter(organization_id=org_id, is_active=True)
        software = Software.objects.filter(organization_id=org_id, is_active=True)
    else:
        network_devices = NetworkDevice.objects.filter(is_active=True)
        endpoint_users = EndpointUser.objects.filter(is_active=True)
        servers = Server.objects.filter(is_active=True)
        peripherals = Peripheral.objects.filter(is_active=True)
        backups = Backup.objects.filter(is_active=True)
        software = Software.objects.filter(is_active=True)

    return Response({
        'network_devices': NetworkDeviceSerializer(network_devices, many=True).data,
        'endpoint_users': EndpointUserSerializer(endpoint_users, many=True).data,
        'servers': ServerSerializer(servers, many=True).data,
        'peripherals': PeripheralSerializer(peripherals, many=True).data,
        'backups': BackupSerializer(backups, many=True).data,
        'software': SoftwareSerializer(software, many=True).data,
    })
