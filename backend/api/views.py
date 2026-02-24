from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db import connection
from django.db.models import Q, Count
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import uuid
import django
import sys
import os
import shutil
from core.models import (
    Organization, Location, Contact, Documentation,
    PasswordEntry, Configuration, NetworkDevice, EndpointUser, Server, Peripheral, Software, Backup, VoIP
)
from core.serializers import (
    NetworkDeviceSerializer, EndpointUserSerializer, ServerSerializer, PeripheralSerializer, SoftwareSerializer, BackupSerializer, VoIPSerializer
)
from core.constants import get_all_choices
from users.models import User


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
def endpoint_counts(request):
    """
    Get counts for all endpoint types filtered by organization.
    This is a lightweight endpoint that returns only counts (not full data)
    for efficient tab badge display.

    Query parameters:
    - organization_id: Required. Filter counts by organization.

    Returns:
    {
        'network_devices': 5,
        'endpoint_users': 11,
        'servers': 3,
        'peripherals': 2,
        'backups': 4,
        'software': 8,
        'voip': 2
    }
    """
    org_id = request.query_params.get('organization_id')

    if not org_id:
        return Response(
            {'error': 'organization_id is required'},
            status=400
        )

    base_filter = {'organization_id': org_id, 'is_active': True}

    return Response({
        'network_devices': NetworkDevice.objects.filter(**base_filter).count(),
        'endpoint_users': EndpointUser.objects.filter(**base_filter).count(),
        'servers': Server.objects.filter(**base_filter).count(),
        'peripherals': Peripheral.objects.filter(**base_filter).count(),
        'backups': Backup.objects.filter(**base_filter).count(),
        'software': Software.objects.filter(**base_filter).count(),
        'voip': VoIP.objects.filter(**base_filter).count(),
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
    org_id = request.query_params.get('organization_id')
    location_id_str = request.query_params.get('location_id')

    # Convert location_id to UUID if provided
    location_id = None
    if location_id_str:
        try:
            location_id = uuid.UUID(location_id_str)
        except (ValueError, TypeError):
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
    # Use prefetch_related to avoid N+1 queries
    if location_id:
        # Software: include if any assigned contact has this location or no location
        # Use a single query with prefetch to get all software with their assignments
        all_software = Software.objects.filter(**base_filter).prefetch_related(
            'software_assignments__contact'
        )
        software_ids = set()
        for sw in all_software:
            # Use prefetched data - no additional queries
            assignments = list(sw.software_assignments.all())
            if not assignments:
                # No assignments - show in all location views
                software_ids.add(sw.id)
            else:
                # Check if any contact has this location or no location
                for assignment in assignments:
                    if assignment.contact.location_id == location_id or assignment.contact.location_id is None:
                        software_ids.add(sw.id)
                        break

        software = Software.objects.filter(id__in=software_ids, **base_filter)

        # VoIP: include if any assigned contact has this location or no location
        all_voip = VoIP.objects.filter(**base_filter).prefetch_related(
            'voip_assignments__contact'
        )
        voip_ids = set()
        for vp in all_voip:
            # Use prefetched data - no additional queries
            assignments = list(vp.voip_assignments.all())
            if not assignments:
                # No assignments - show in all location views
                voip_ids.add(vp.id)
            else:
                # Check if any contact has this location or no location
                for assignment in assignments:
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


@api_view(['GET'])
@permission_classes([IsAdminUser])
def system_health(request):
    """
    Comprehensive system health check for administrators.
    Returns detailed information about system status, database, users, and data.
    """
    health_data = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'checks': {},
    }

    # 1. Database connectivity check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_name = settings.DATABASES['default'].get('NAME', 'N/A')
        # Convert Path objects to string for JSON serialization (Windows compatibility)
        if hasattr(db_name, '__fspath__'):
            db_name = str(db_name)
        health_data['checks']['database'] = {
            'status': 'healthy',
            'engine': settings.DATABASES['default']['ENGINE'].split('.')[-1],
            'name': db_name,
        }
    except Exception as e:
        health_data['checks']['database'] = {
            'status': 'unhealthy',
            'error': str(e),
        }
        health_data['status'] = 'unhealthy'

    # 2. Version information
    health_data['checks']['versions'] = {
        'status': 'healthy',
        'django': django.get_version(),
        'python': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'environment': os.environ.get('ENVIRONMENT', settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else 'unknown'),
        'debug_mode': settings.DEBUG,
    }

    # 3. User statistics - Use aggregation to reduce queries
    try:
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        # Single aggregation query for user stats
        user_stats = User.objects.aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(is_active=True)),
            admin=Count('id', filter=Q(is_staff=True)),
            locked=Count('id', filter=Q(locked_until__gt=now)),
            twofa_enabled=Count('id', filter=Q(twofa_enabled=True)),
            recent_logins_24h=Count('id', filter=Q(last_login__gte=last_24h)),
            recent_logins_7d=Count('id', filter=Q(last_login__gte=last_7d)),
            never_logged_in=Count('id', filter=Q(last_login__isnull=True)),
        )

        total_users = user_stats['total']
        active_users = user_stats['active']
        admin_users = user_stats['admin']
        locked_users = user_stats['locked']
        twofa_enabled = user_stats['twofa_enabled']
        recent_logins_24h = user_stats['recent_logins_24h']
        recent_logins_7d = user_stats['recent_logins_7d']
        never_logged_in = user_stats['never_logged_in']

        health_data['checks']['users'] = {
            'status': 'healthy',
            'total': total_users,
            'active': active_users,
            'inactive': total_users - active_users,
            'admins': admin_users,
            'locked_accounts': locked_users,
            'twofa_enabled': twofa_enabled,
            'twofa_disabled': total_users - twofa_enabled,
            'twofa_percentage': round((twofa_enabled / total_users * 100) if total_users > 0 else 0, 1),
            'recent_logins_24h': recent_logins_24h,
            'recent_logins_7d': recent_logins_7d,
            'never_logged_in': never_logged_in,
        }

        # Add warning if locked accounts exist
        if locked_users > 0:
            health_data['checks']['users']['status'] = 'warning'
    except Exception as e:
        health_data['checks']['users'] = {
            'status': 'unhealthy',
            'error': str(e),
        }

    # 4. Data statistics - Use aggregation to reduce queries
    try:
        # Use a helper to get active/deleted counts in single query per model
        # Use all_objects to include soft-deleted records in the count
        def get_counts(model):
            result = model.all_objects.aggregate(
                active=Count('id', filter=Q(deleted_at__isnull=True)),
                deleted=Count('id', filter=Q(deleted_at__isnull=False)),
            )
            return result['active'], result['deleted']

        # Get counts for all models (13 queries instead of 26)
        org_active, org_deleted = get_counts(Organization)
        loc_active, loc_deleted = get_counts(Location)
        contact_active, contact_deleted = get_counts(Contact)
        doc_active, doc_deleted = get_counts(Documentation)
        pwd_active, pwd_deleted = get_counts(PasswordEntry)
        config_active, config_deleted = get_counts(Configuration)
        netdev_active, netdev_deleted = get_counts(NetworkDevice)
        endpoint_active, endpoint_deleted = get_counts(EndpointUser)
        server_active, server_deleted = get_counts(Server)
        peripheral_active, peripheral_deleted = get_counts(Peripheral)
        software_active, software_deleted = get_counts(Software)
        backup_active, backup_deleted = get_counts(Backup)
        voip_active, voip_deleted = get_counts(VoIP)

        active_counts = {
            'organizations': org_active,
            'locations': loc_active,
            'contacts': contact_active,
            'documentations': doc_active,
            'passwords': pwd_active,
            'configurations': config_active,
            'network_devices': netdev_active,
            'endpoint_users': endpoint_active,
            'servers': server_active,
            'peripherals': peripheral_active,
            'software': software_active,
            'backups': backup_active,
            'voip': voip_active,
        }

        deleted_counts = {
            'organizations': org_deleted,
            'locations': loc_deleted,
            'contacts': contact_deleted,
            'documentations': doc_deleted,
            'passwords': pwd_deleted,
            'configurations': config_deleted,
            'network_devices': netdev_deleted,
            'endpoint_users': endpoint_deleted,
            'servers': server_deleted,
            'peripherals': peripheral_deleted,
            'software': software_deleted,
            'backups': backup_deleted,
            'voip': voip_deleted,
        }

        total_active = sum(active_counts.values())
        total_deleted = sum(deleted_counts.values())

        health_data['checks']['data'] = {
            'status': 'healthy',
            'active_records': active_counts,
            'deleted_records': deleted_counts,
            'total_active': total_active,
            'total_deleted': total_deleted,
        }
    except Exception as e:
        health_data['checks']['data'] = {
            'status': 'unhealthy',
            'error': str(e),
        }

    # 5. Security configuration
    health_data['checks']['security'] = {
        'status': 'healthy',
        'https_enforced': not settings.DEBUG and getattr(settings, 'SECURE_SSL_REDIRECT', False),
        'hsts_enabled': getattr(settings, 'SECURE_HSTS_SECONDS', 0) > 0,
        'csrf_protection': True,
        'session_cookie_secure': getattr(settings, 'SESSION_COOKIE_SECURE', False),
        'rate_limiting': 'DEFAULT_THROTTLE_RATES' in getattr(settings, 'REST_FRAMEWORK', {}),
    }

    # 6. Storage check (database file for SQLite)
    try:
        db_engine = settings.DATABASES['default']['ENGINE']
        if 'sqlite3' in db_engine:
            db_path = settings.DATABASES['default']['NAME']
            if os.path.exists(db_path):
                db_size = os.path.getsize(db_path)
                health_data['checks']['storage'] = {
                    'status': 'healthy',
                    'type': 'sqlite',
                    'database_size_mb': round(db_size / (1024 * 1024), 2),
                }
            else:
                health_data['checks']['storage'] = {
                    'status': 'warning',
                    'type': 'sqlite',
                    'message': 'Database file not found',
                }
        else:
            # PostgreSQL - get database size
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT pg_database_size(current_database())")
                    db_size = cursor.fetchone()[0]
                health_data['checks']['storage'] = {
                    'status': 'healthy',
                    'type': 'postgresql',
                    'database_size_mb': round(db_size / (1024 * 1024), 2),
                }
            except Exception:
                health_data['checks']['storage'] = {
                    'status': 'healthy',
                    'type': 'postgresql',
                    'message': 'Size query not available',
                }
    except Exception as e:
        health_data['checks']['storage'] = {
            'status': 'warning',
            'error': str(e),
        }

    # 7. Disk space check
    try:
        # Get disk usage for the root filesystem or current working directory
        disk_path = '/'
        if os.name == 'nt':  # Windows
            disk_path = os.path.splitdrive(os.getcwd())[0] + '\\'

        disk_usage = shutil.disk_usage(disk_path)
        total_gb = disk_usage.total / (1024 ** 3)
        used_gb = disk_usage.used / (1024 ** 3)
        free_gb = disk_usage.free / (1024 ** 3)
        used_percent = (disk_usage.used / disk_usage.total) * 100
        free_percent = (disk_usage.free / disk_usage.total) * 100

        # Determine status based on free space percentage
        if free_percent < 10:
            disk_status = 'unhealthy'
        elif free_percent < 20:
            disk_status = 'warning'
        else:
            disk_status = 'healthy'

        health_data['checks']['disk_space'] = {
            'status': disk_status,
            'path': disk_path,
            'total_gb': round(total_gb, 2),
            'used_gb': round(used_gb, 2),
            'free_gb': round(free_gb, 2),
            'used_percent': round(used_percent, 1),
            'free_percent': round(free_percent, 1),
        }
    except Exception as e:
        health_data['checks']['disk_space'] = {
            'status': 'warning',
            'error': str(e),
        }

    # Determine overall status
    statuses = [check.get('status', 'healthy') for check in health_data['checks'].values()]
    if 'unhealthy' in statuses:
        health_data['status'] = 'unhealthy'
    elif 'warning' in statuses:
        health_data['status'] = 'warning'

    return Response(health_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_choices(request):
    """
    Get all available choices/enums for the application.

    This is the Single Source of Truth for all dropdown options, categories,
    and types used throughout the application. Frontend should fetch this
    once on load and cache in context/store.

    Returns a dictionary with choice names as keys and arrays of
    {value, label} objects as values.

    Example response:
    {
        "documentation_category": [
            {"value": "procedure", "label": "Procedure"},
            {"value": "configuration", "label": "Configuration"},
            ...
        ],
        "server_type": [
            {"value": "physical", "label": "Physical Server"},
            ...
        ],
        ...
    }
    """
    return Response(get_all_choices())
