"""
URL configuration for TechVault project.
"""
from django.contrib import admin
from django.urls import path, include
from users.auth_views import login_with_2fa

urlpatterns = [
    path('admin/', admin.site.urls),
    # Custom login endpoint with 2FA support (overrides dj-rest-auth login)
    path('api/auth/login/', login_with_2fa, name='rest_login'),
    path('api/auth/', include('dj_rest_auth.urls')),
    # Registration disabled - users must be created by admins
    # path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/', include('api.urls')),
    path('api/reports/', include('reports.urls')),
]
