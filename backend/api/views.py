from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db import connection
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import django
import sys
import os
from core.models import (
    Organization, Location, Contact, Documentation,
    PasswordEntry, Configuration, NetworkDevice, EndpointUser, Server, Peripheral, Software, Backup, VoIP
)
from core.serializers import (
    NetworkDeviceSerializer, EndpointUserSerializer, ServerSerializer, PeripheralSerializer, SoftwareSerializer, BackupSerializer, VoIPSerializer
)
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

    # 3. User statistics
    try:
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        admin_users = User.objects.filter(is_staff=True).count()
        locked_users = User.objects.filter(locked_until__gt=timezone.now()).count()
        twofa_enabled = User.objects.filter(twofa_enabled=True).count()

        # Recent activity
        last_24h = timezone.now() - timedelta(hours=24)
        last_7d = timezone.now() - timedelta(days=7)
        recent_logins_24h = User.objects.filter(last_login__gte=last_24h).count()
        recent_logins_7d = User.objects.filter(last_login__gte=last_7d).count()
        never_logged_in = User.objects.filter(last_login__isnull=True).count()

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

    # 4. Data statistics
    try:
        # Active records
        active_counts = {
            'organizations': Organization.objects.filter(is_active=True).count(),
            'locations': Location.objects.filter(is_active=True).count(),
            'contacts': Contact.objects.filter(is_active=True).count(),
            'documentations': Documentation.objects.filter(is_active=True).count(),
            'passwords': PasswordEntry.objects.filter(is_active=True).count(),
            'configurations': Configuration.objects.filter(is_active=True).count(),
            'network_devices': NetworkDevice.objects.filter(is_active=True).count(),
            'endpoint_users': EndpointUser.objects.filter(is_active=True).count(),
            'servers': Server.objects.filter(is_active=True).count(),
            'peripherals': Peripheral.objects.filter(is_active=True).count(),
            'software': Software.objects.filter(is_active=True).count(),
            'backups': Backup.objects.filter(is_active=True).count(),
            'voip': VoIP.objects.filter(is_active=True).count(),
        }

        # Soft-deleted records
        deleted_counts = {
            'organizations': Organization.objects.filter(is_active=False).count(),
            'locations': Location.objects.filter(is_active=False).count(),
            'contacts': Contact.objects.filter(is_active=False).count(),
            'documentations': Documentation.objects.filter(is_active=False).count(),
            'passwords': PasswordEntry.objects.filter(is_active=False).count(),
            'configurations': Configuration.objects.filter(is_active=False).count(),
            'network_devices': NetworkDevice.objects.filter(is_active=False).count(),
            'endpoint_users': EndpointUser.objects.filter(is_active=False).count(),
            'servers': Server.objects.filter(is_active=False).count(),
            'peripherals': Peripheral.objects.filter(is_active=False).count(),
            'software': Software.objects.filter(is_active=False).count(),
            'backups': Backup.objects.filter(is_active=False).count(),
            'voip': VoIP.objects.filter(is_active=False).count(),
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

    # Determine overall status
    statuses = [check.get('status', 'healthy') for check in health_data['checks'].values()]
    if 'unhealthy' in statuses:
        health_data['status'] = 'unhealthy'
    elif 'warning' in statuses:
        health_data['status'] = 'warning'

    return Response(health_data)
