"""
Custom authentication views for TechVault with 2FA support and account lockout.
"""
import pyotp
import logging
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from django.middleware.csrf import get_token
from dj_rest_auth.jwt_auth import set_jwt_cookies, unset_jwt_cookies
from dj_rest_auth.app_settings import api_settings as rest_auth_settings
from users.throttling import LoginRateThrottle
from users.utils import hash_backup_code, consume_backup_code, get_client_ip  # noqa: F401 (hash_backup_code re-exported)

User = get_user_model()
security_logger = logging.getLogger('security')


def get_tokens_for_user(user):
    """Generate JWT tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    }


def _login_response(request, user, extra=None):
    """
    Build the successful-login response.

    Tokens are set as HttpOnly cookies so browser JavaScript never handles them
    (the browser client relies on the cookies). They are also returned in the body
    for non-browser API clients that use the Authorization header.
    """
    from core.models import AuditLog

    tokens = get_tokens_for_user(user)
    if extra:
        tokens.update(extra)
    response = Response(tokens, status=status.HTTP_200_OK)
    set_jwt_cookies(response, tokens['access_token'], tokens['refresh_token'])
    # Make sure the browser has a CSRF cookie: cookie-authenticated requests need it.
    get_token(request)
    AuditLog.log(
        user=user, action='login', entity_type='User', entity_id=user.pk,
        entity_name=user.email, ip_address=get_client_ip(request),
    )
    return response


@api_view(['POST'])
@authentication_classes([])  # a stale/expired auth cookie must not block logging out
@permission_classes([AllowAny])
def logout(request):
    """
    Log out: blacklist the refresh token (so it cannot be reused) and clear auth cookies.
    The refresh token is taken from the request body or, for browsers, the cookie.
    """
    from rest_framework_simplejwt.exceptions import TokenError

    raw_refresh = request.data.get('refresh') or request.COOKIES.get(rest_auth_settings.JWT_AUTH_REFRESH_COOKIE)
    if raw_refresh:
        try:
            token = RefreshToken(raw_refresh)
            token.blacklist()
            user = User.objects.filter(pk=token.get('user_id')).first()
            if user:
                from core.models import AuditLog
                AuditLog.log(
                    user=user, action='logout', entity_type='User', entity_id=user.pk,
                    entity_name=user.email, ip_address=get_client_ip(request),
                )
        except TokenError:
            pass  # already expired/blacklisted - nothing to revoke
    response = Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
    unset_jwt_cookies(response)
    return response


@api_view(['POST'])
@authentication_classes([])  # a stale/expired auth cookie must not block logging in
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
def login_with_2fa(request):
    """
    Custom login endpoint that handles 2FA with account lockout protection.

    Security features:
    - Rate limiting (5 attempts/minute via throttle)
    - Account lockout after 5 failed attempts (15 minute lockout)
    - Audit logging of login attempts

    Step 1: POST with email + password
    - If user has 2FA enabled, return requires_2fa=True
    - If user doesn't have 2FA, return tokens immediately

    Step 2: POST with email + password + twofa_token
    - Verify 2FA token and return tokens if valid
    """
    email = request.data.get('email')
    password = request.data.get('password')
    raw_twofa_token = str(request.data.get('twofa_token') or '')
    twofa_token = raw_twofa_token.strip().replace('-', '').replace(' ', '')
    client_ip = get_client_ip(request) or 'unknown'

    # Validate required fields
    if not email or not password:
        return Response(
            {'error': 'Email and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if user exists and is locked out (before authentication)
    try:
        user_check = User.objects.get(email=email)
        if user_check.is_locked():
            security_logger.warning(
                f"Login attempt on locked account: email={email}, ip={client_ip}"
            )
            return Response(
                {'error': 'Account is temporarily locked due to too many failed login attempts. Please try again later.'},
                status=status.HTTP_403_FORBIDDEN
            )
    except User.DoesNotExist:
        pass  # Continue with authentication to avoid user enumeration

    # Authenticate user with email and password
    user = authenticate(request=request, username=email, password=password)

    if not user:
        # Log failed attempt and update lockout counter
        try:
            user_obj = User.objects.get(email=email)
            user_obj.record_failed_login()
            security_logger.warning(
                f"Failed login attempt: email={email}, ip={client_ip}, "
                f"attempts={user_obj.failed_login_attempts}"
            )
            if user_obj.is_locked():
                return Response(
                    {'error': 'Account is temporarily locked due to too many failed login attempts. Please try again later.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except User.DoesNotExist:
            # Log but don't reveal user doesn't exist
            security_logger.warning(
                f"Failed login attempt (unknown user): email={email}, ip={client_ip}"
            )

        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Check if user is active
    if not user.is_active:
        security_logger.warning(
            f"Login attempt on disabled account: email={email}, ip={client_ip}"
        )
        return Response(
            {'error': 'Account is disabled'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # If 2FA is not enabled, return tokens but indicate setup is required
    if not user.twofa_enabled:
        # Reset failed attempts on successful login and update last_login
        user.reset_failed_login_attempts()
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        security_logger.info(
            f"Successful login (2FA not enabled): email={email}, ip={client_ip}"
        )
        return _login_response(request, user, {
            'requires_2fa_setup': True,
            'message': 'You must enable Two-Factor Authentication. Please set up 2FA to continue using the application.',
            'setup_url': '/api/auth/2fa/setup/',
        })

    # If 2FA is enabled but no token provided, ask for it
    if not twofa_token:
        return Response({
            'requires_2fa': True,
            'message': 'Please provide your 2FA token',
            'email': email  # Return email so frontend can store it for next request
        }, status=status.HTTP_200_OK)

    # Verify 2FA token
    totp = pyotp.TOTP(user.twofa_secret)

    # Try TOTP verification first
    if totp.verify(twofa_token, valid_window=1):
        # Reset failed attempts on successful login and update last_login
        user.reset_failed_login_attempts()
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        security_logger.info(
            f"Successful login with 2FA: email={email}, ip={client_ip}"
        )
        return _login_response(request, user)

    # Check if it's a backup code (separators and case are ignored)
    if consume_backup_code(user, raw_twofa_token):
        # Used backup code has been removed; update last_login
        user.reset_failed_login_attempts()
        user.last_login = timezone.now()
        user.save()

        security_logger.info(
            f"Successful login with backup code: email={email}, ip={client_ip}, "
            f"remaining_codes={len(user.twofa_backup_codes)}"
        )

        return _login_response(request, user, {
            'backup_code_used': True,
            'remaining_backup_codes': len(user.twofa_backup_codes),
            'warning': f'Backup code used. You have {len(user.twofa_backup_codes)} backup codes remaining.',
        })

    # Invalid 2FA token - count as failed attempt
    user.record_failed_login()
    security_logger.warning(
        f"Failed 2FA attempt: email={email}, ip={client_ip}, "
        f"attempts={user.failed_login_attempts}"
    )

    if user.is_locked():
        return Response(
            {'error': 'Account is temporarily locked due to too many failed login attempts. Please try again later.'},
            status=status.HTTP_403_FORBIDDEN
        )

    return Response(
        {'error': 'Invalid 2FA token or backup code'},
        status=status.HTTP_401_UNAUTHORIZED
    )
