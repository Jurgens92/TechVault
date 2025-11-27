"""
API URL Configuration for TechVault.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from users.views import UserProfileView, UserManagementViewSet
from core.views import (
    OrganizationViewSet, LocationViewSet, ContactViewSet,
    DocumentationViewSet, PasswordEntryViewSet, ConfigurationViewSet,
    NetworkDeviceViewSet, EndpointUserViewSet, ServerViewSet, PeripheralViewSet, SoftwareViewSet, BackupViewSet
)
from .views import dashboard_stats, diagram_data

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
router.register(r'users', UserManagementViewSet, basename='user')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # Dashboard endpoints
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),

    # Diagram endpoints
    path('diagram/data/', diagram_data, name='diagram-data'),

    # User endpoints
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),

    # JWT token endpoints
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),
]
