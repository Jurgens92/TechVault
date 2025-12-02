from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import (
    Organization, Location, Contact, Documentation,
    PasswordEntry, Configuration, NetworkDevice, EndpointUser, Server, Peripheral, Software, Backup, VoIP
)
from core.serializers import (
    NetworkDeviceSerializer, EndpointUserSerializer, ServerSerializer, PeripheralSerializer, SoftwareSerializer, BackupSerializer, VoIPSerializer
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
    Supports filtering by organization and location.

    Query parameters:
    - organization_id: Filter by organization
    - location_id: Filter by location (includes unassigned items with location=null)
    """
    from django.db.models import Q
    import uuid

    org_id = request.query_params.get('organization_id')
    location_id_str = request.query_params.get('location_id')

    # Convert location_id to UUID if provided
    location_id = None
    if location_id_str:
        try:
            location_id = uuid.UUID(location_id_str)
        except (ValueError, AttributeError):
            location_id = None

    # Base filters
    base_filter = {'is_active': True}
    if org_id:
        base_filter['organization_id'] = org_id

    # Filter physical devices (include unassigned items if location_id is specified)
    if location_id:
        # Include items with the specified location OR unassigned items (location=null)
        location_filter = Q(location_id=location_id) | Q(location__isnull=True)
        network_devices = NetworkDevice.objects.filter(**base_filter).filter(location_filter)
        endpoint_users = EndpointUser.objects.filter(**base_filter).filter(location_filter)
        servers = Server.objects.filter(**base_filter).filter(location_filter)
        peripherals = Peripheral.objects.filter(**base_filter).filter(location_filter)
        backups = Backup.objects.filter(**base_filter).filter(location_filter)
    else:
        # No location filter - show all
        network_devices = NetworkDevice.objects.filter(**base_filter)
        endpoint_users = EndpointUser.objects.filter(**base_filter)
        servers = Server.objects.filter(**base_filter)
        peripherals = Peripheral.objects.filter(**base_filter)
        backups = Backup.objects.filter(**base_filter)

    # Filter Software and VoIP based on assigned contacts' locations
    if location_id:
        # Software: include if any assigned contact has this location or no location
        software_ids = set()
        all_software = Software.objects.filter(**base_filter)
        for sw in all_software:
            # Get all assigned contacts for this software
            assigned_contacts = sw.software_assignments.select_related('contact').all()
            if not assigned_contacts.exists():
                # No assignments - show in all location views
                software_ids.add(sw.id)
            else:
                # Check if any contact has this location or no location
                for assignment in assigned_contacts:
                    if assignment.contact.location_id == location_id or assignment.contact.location_id is None:
                        software_ids.add(sw.id)
                        break

        software = Software.objects.filter(id__in=software_ids, **base_filter)

        # VoIP: include if any assigned contact has this location or no location
        voip_ids = set()
        all_voip = VoIP.objects.filter(**base_filter)
        for vp in all_voip:
            # Get all assigned contacts for this voip
            assigned_contacts = vp.voip_assignments.select_related('contact').all()
            if not assigned_contacts.exists():
                # No assignments - show in all location views
                voip_ids.add(vp.id)
            else:
                # Check if any contact has this location or no location
                for assignment in assigned_contacts:
                    if assignment.contact.location_id == location_id or assignment.contact.location_id is None:
                        voip_ids.add(vp.id)
                        break

        voip = VoIP.objects.filter(id__in=voip_ids, **base_filter)
    else:
        # No location filter - show all
        software = Software.objects.filter(**base_filter)
        voip = VoIP.objects.filter(**base_filter)

    return Response({
        'network_devices': NetworkDeviceSerializer(network_devices, many=True).data,
        'endpoint_users': EndpointUserSerializer(endpoint_users, many=True).data,
        'servers': ServerSerializer(servers, many=True).data,
        'peripherals': PeripheralSerializer(peripherals, many=True).data,
        'backups': BackupSerializer(backups, many=True).data,
        'software': SoftwareSerializer(software, many=True).data,
        'voip': VoIPSerializer(voip, many=True).data,
    })
