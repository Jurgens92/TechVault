"""
Custom authentication views for TechVault with 2FA support.
"""
import pyotp
import hashlib
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()


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
def login_with_2fa(request):
    """
    Custom login endpoint that handles 2FA.

    Step 1: POST with email + password
    - If user has 2FA enabled, return requires_2fa=True
    - If user doesn't have 2FA, return tokens immediately

    Step 2: POST with email + password + twofa_token
    - Verify 2FA token and return tokens if valid
    """
    email = request.data.get('email')
    password = request.data.get('password')
    twofa_token = request.data.get('twofa_token', '').strip().replace('-', '').replace(' ', '')

    # Validate required fields
    if not email or not password:
        return Response(
            {'error': 'Email and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Authenticate user with email and password
    user = authenticate(request=request, username=email, password=password)

    if not user:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Check if user is active
    if not user.is_active:
        return Response(
            {'error': 'Account is disabled'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # If 2FA is not enabled, return tokens immediately
    if not user.twofa_enabled:
        tokens = get_tokens_for_user(user)
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
        tokens = get_tokens_for_user(user)
        return Response(tokens, status=status.HTTP_200_OK)

    # Check if it's a backup code
    token_hash = hash_backup_code(twofa_token.upper())
    if token_hash in user.twofa_backup_codes:
        # Remove used backup code
        user.twofa_backup_codes.remove(token_hash)
        user.save()

        tokens = get_tokens_for_user(user)
        tokens['backup_code_used'] = True
        tokens['remaining_backup_codes'] = len(user.twofa_backup_codes)
        tokens['warning'] = f'Backup code used. You have {len(user.twofa_backup_codes)} backup codes remaining.'

        return Response(tokens, status=status.HTTP_200_OK)

    # Invalid 2FA token
    return Response(
        {'error': 'Invalid 2FA token or backup code'},
        status=status.HTTP_401_UNAUTHORIZED
    )
