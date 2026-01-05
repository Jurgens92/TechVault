"""
Custom authentication views for TechVault with 2FA support and account lockout.
"""
import pyotp
import hashlib
import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from users.throttling import LoginRateThrottle

User = get_user_model()
security_logger = logging.getLogger('security')


def hash_backup_code(code):
    """Hash a backup code for comparison."""
    return hashlib.sha256(code.encode()).hexdigest()


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


@api_view(['POST'])
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
    twofa_token = request.data.get('twofa_token', '').strip().replace('-', '').replace(' ', '')
    client_ip = request.META.get('REMOTE_ADDR', 'unknown')

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
        tokens = get_tokens_for_user(user)
        tokens['requires_2fa_setup'] = True
        tokens['message'] = 'You must enable Two-Factor Authentication. Please set up 2FA to continue using the application.'
        tokens['setup_url'] = '/api/auth/2fa/setup/'
        return Response(tokens, status=status.HTTP_200_OK)

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
        tokens = get_tokens_for_user(user)
        return Response(tokens, status=status.HTTP_200_OK)

    # Check if it's a backup code
    token_hash = hash_backup_code(twofa_token.upper())
    if token_hash in user.twofa_backup_codes:
        # Remove used backup code and update last_login
        user.twofa_backup_codes.remove(token_hash)
        user.reset_failed_login_attempts()
        user.last_login = timezone.now()
        user.save()

        security_logger.info(
            f"Successful login with backup code: email={email}, ip={client_ip}, "
            f"remaining_codes={len(user.twofa_backup_codes)}"
        )

        tokens = get_tokens_for_user(user)
        tokens['backup_code_used'] = True
        tokens['remaining_backup_codes'] = len(user.twofa_backup_codes)
        tokens['warning'] = f'Backup code used. You have {len(user.twofa_backup_codes)} backup codes remaining.'

        return Response(tokens, status=status.HTTP_200_OK)

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
