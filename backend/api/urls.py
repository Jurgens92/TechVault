"""
API URL Configuration for TechVault.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from users.views import UserProfileView
from core.views import (
    OrganizationViewSet, LocationViewSet, ContactViewSet,
    DocumentationViewSet, PasswordEntryViewSet, ConfigurationViewSet
)
from .views import dashboard_stats

app_name = 'api'

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'documentations', DocumentationViewSet, basename='documentation')
router.register(r'passwords', PasswordEntryViewSet, basename='password')
router.register(r'configurations', ConfigurationViewSet, basename='configuration')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # Dashboard endpoints
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),

    # User endpoints
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),

    # JWT token endpoints
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),
]
