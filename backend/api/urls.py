"""
API URL Configuration for TechVault.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from users.views import UserProfileView

app_name = 'api'

urlpatterns = [
    # User endpoints
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),

    # JWT token endpoints
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),
]
