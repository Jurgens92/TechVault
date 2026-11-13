"""
URL configuration for TechVault project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from users.auth_views import login_with_2fa, logout
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Custom login endpoint with 2FA support (overrides dj-rest-auth login)
    path('api/auth/login/', login_with_2fa, name='rest_login'),
    # Custom logout: revokes the refresh token and clears auth cookies
    path('api/auth/logout/', logout, name='rest_logout'),
    path('api/auth/', include('dj_rest_auth.urls')),
    # Registration disabled - users must be created by admins
    # path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/', include('api.urls')),
    path('api/reports/', include('reports.urls')),

    # OpenAPI Schema - Single Source of Truth for API Documentation
    # Frontend can auto-generate TypeScript types from /api/schema/
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Django admin bypasses 2FA and account lockout, so it is opt-in (see settings).
if settings.ENABLE_DJANGO_ADMIN:
    urlpatterns.insert(0, path('admin/', admin.site.urls))
