"""
Middleware to enforce 2FA for all authenticated users.

This middleware checks if authenticated users have 2FA enabled.
If not, it only allows access to 2FA setup endpoints and blocks all other API calls.
"""

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class Enforce2FAMiddleware(MiddlewareMixin):
    """
    Middleware that enforces 2FA for all authenticated users.

    Users without 2FA enabled can only access:
    - All authentication endpoints (/api/auth/*) - login, logout, register, 2FA setup, token refresh, etc.
    - User account management endpoints (/api/user/*) - view/edit profile, change password, etc.
    - Django admin panel (/admin/)

    All other endpoints (business data like /api/organizations/, /api/devices/, etc.)
    are blocked until 2FA is enabled.
    """

    # Endpoints that are always allowed (public or 2FA setup)
    ALLOWED_PATHS = [
        '/api/auth/',  # Allow all auth endpoints (login, logout, register, token refresh, etc.)
        '/api/user/',  # Allow user profile access (needed to view own profile before setting up 2FA)
        '/admin/',  # Allow Django admin access
    ]

    def process_request(self, request):
        """
        Check if the user is authenticated and has 2FA enabled.
        Block access to endpoints if 2FA is not enabled.
        """

        # Skip middleware for allowed paths
        path = request.path_info
        if any(path.startswith(allowed) for allowed in self.ALLOWED_PATHS):
            return None

        # Skip for static/media files
        if path.startswith('/static/') or path.startswith('/media/'):
            return None

        # Try to authenticate using JWT
        jwt_authenticator = JWTAuthentication()
        try:
            # Attempt to authenticate the request
            auth_result = jwt_authenticator.authenticate(request)

            # If authentication successful, check 2FA status
            if auth_result is not None:
                user, token = auth_result

                # Check if user has 2FA enabled
                if not user.twofa_enabled:
                    return JsonResponse({
                        'error': '2FA is required',
                        'message': 'You must enable Two-Factor Authentication to access this resource. Please set up 2FA first.',
                        'requires_2fa_setup': True,
                        'setup_url': '/api/auth/2fa/setup/'
                    }, status=403)

        except AuthenticationFailed:
            # If authentication fails, let the view handle it
            pass
        except Exception:
            # If any other error, let the view handle it
            pass

        # Allow request to continue
        return None
