"""
API URL Configuration for TechVault.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from users.views import UserProfileView, UserManagementViewSet
from users.auth_views import login_with_2fa
from users.twofa_views import (
    setup_2fa, enable_2fa, disable_2fa, verify_2fa_token,
    regenerate_backup_codes, get_2fa_status
)
from core.views import (
    OrganizationViewSet, LocationViewSet, ContactViewSet,
    DocumentationViewSet, PasswordEntryViewSet, ConfigurationViewSet,
    NetworkDeviceViewSet, EndpointUserViewSet, ServerViewSet, PeripheralViewSet, SoftwareViewSet, BackupViewSet, VoIPViewSet
)
from .views import dashboard_stats, diagram_data, system_health

app_name = 'api'

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'documentations', DocumentationViewSet, basename='documentation')
router.register(r'passwords', PasswordEntryViewSet, basename='password')
router.register(r'configurations', ConfigurationViewSet, basename='configuration')
router.register(r'network-devices', NetworkDeviceViewSet, basename='network-device')
router.register(r'endpoint-users', EndpointUserViewSet, basename='endpoint-user')
router.register(r'servers', ServerViewSet, basename='server')
router.register(r'peripherals', PeripheralViewSet, basename='peripheral')
router.register(r'software', SoftwareViewSet, basename='software')
router.register(r'backups', BackupViewSet, basename='backup')
router.register(r'voip', VoIPViewSet, basename='voip')
router.register(r'users', UserManagementViewSet, basename='user')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # Dashboard endpoints
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),

    # Diagram endpoints
    path('diagram/data/', diagram_data, name='diagram-data'),

    # Admin system health endpoint
    path('admin/health/', system_health, name='system-health'),

    # User endpoints
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),

    # Auth endpoints
    path('auth/login/', login_with_2fa, name='login'),

    # Two-Factor Authentication endpoints
    path('auth/2fa/status/', get_2fa_status, name='2fa-status'),
    path('auth/2fa/setup/', setup_2fa, name='2fa-setup'),
    path('auth/2fa/enable/', enable_2fa, name='2fa-enable'),
    path('auth/2fa/disable/', disable_2fa, name='2fa-disable'),
    path('auth/2fa/verify/', verify_2fa_token, name='2fa-verify'),
    path('auth/2fa/backup-codes/regenerate/', regenerate_backup_codes, name='2fa-regenerate-backup-codes'),

    # JWT token endpoints
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),
]
