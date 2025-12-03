"""
Two-Factor Authentication (2FA) views for TechVault.
Implements TOTP-based 2FA with QR code setup and backup codes.
"""
import base64
import hashlib
import io
import pyotp
import qrcode
import secrets
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_backup_codes(count=10):
    """Generate secure backup codes for 2FA recovery."""
    codes = []
    for _ in range(count):
        code = '-'.join([secrets.token_hex(2).upper() for _ in range(3)])
        codes.append(code)
    return codes


def hash_backup_code(code):
    """Hash a backup code for secure storage."""
    return hashlib.sha256(code.encode()).hexdigest()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_2fa(request):
    """
    Generate a new TOTP secret and return QR code for 2FA setup.
    Does not enable 2FA - user must verify with enable_2fa endpoint.
    """
    user = request.user

    # Generate a new TOTP secret
    secret = pyotp.random_base32()

    # Create provisioning URI for authenticator apps
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user.email,
        issuer_name='TechVault'
    )

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert image to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

    # Store secret temporarily (not enabled yet)
    user.twofa_secret = secret
    user.save()

    return Response({
        'secret': secret,
        'qr_code': f'data:image/png;base64,{qr_code_base64}',
        'message': 'Scan the QR code with your authenticator app, then verify with a token to enable 2FA.'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enable_2fa(request):
    """
    Verify TOTP token and enable 2FA for the user.
    Also generates backup codes.
    """
    user = request.user
    token = request.data.get('token')

    if not token:
        return Response(
            {'error': 'Token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not user.twofa_secret:
        return Response(
            {'error': 'Please set up 2FA first using the setup endpoint'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Verify the token
    totp = pyotp.TOTP(user.twofa_secret)
    if not totp.verify(token, valid_window=1):
        return Response(
            {'error': 'Invalid token. Please try again.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Generate backup codes
    backup_codes = generate_backup_codes()
    hashed_codes = [hash_backup_code(code) for code in backup_codes]

    # Enable 2FA
    user.twofa_enabled = True
    user.twofa_backup_codes = hashed_codes
    user.save()

    return Response({
        'message': '2FA enabled successfully',
        'backup_codes': backup_codes,
        'warning': 'Save these backup codes in a secure location. They will not be shown again.'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_2fa(request):
    """
    Disable 2FA for the user.
    Requires current password for security.
    """
    user = request.user
    password = request.data.get('password')

    if not password:
        return Response(
            {'error': 'Password is required to disable 2FA'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not user.check_password(password):
        return Response(
            {'error': 'Invalid password'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not user.twofa_enabled:
        return Response(
            {'error': '2FA is not enabled'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Disable 2FA
    user.twofa_enabled = False
    user.twofa_secret = None
    user.twofa_backup_codes = []
    user.save()

    return Response({
        'message': '2FA disabled successfully'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_2fa_token(request):
    """
    Verify a 2FA token (TOTP or backup code).
    Used during login or for verification purposes.
    """
    user = request.user
    token = request.data.get('token', '').strip().replace('-', '').replace(' ', '')

    if not token:
        return Response(
            {'error': 'Token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not user.twofa_enabled:
        return Response(
            {'error': '2FA is not enabled for this user'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Try TOTP first
    totp = pyotp.TOTP(user.twofa_secret)
    if totp.verify(token, valid_window=1):
        return Response({
            'valid': True,
            'message': 'Token verified successfully'
        })

    # Check if it's a backup code (remove dashes for comparison)
    token_hash = hash_backup_code(token.upper())
    if token_hash in user.twofa_backup_codes:
        # Remove used backup code
        user.twofa_backup_codes.remove(token_hash)
        user.save()

        remaining = len(user.twofa_backup_codes)
        return Response({
            'valid': True,
            'message': 'Backup code verified successfully',
            'backup_code_used': True,
            'remaining_backup_codes': remaining,
            'warning': f'You have {remaining} backup codes remaining. Consider generating new ones.'
        })

    return Response(
        {'valid': False, 'error': 'Invalid token or backup code'},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def regenerate_backup_codes(request):
    """
    Generate new backup codes for the user.
    Requires password and replaces all existing backup codes.
    """
    user = request.user
    password = request.data.get('password')

    if not password:
        return Response(
            {'error': 'Password is required to regenerate backup codes'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not user.check_password(password):
        return Response(
            {'error': 'Invalid password'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not user.twofa_enabled:
        return Response(
            {'error': '2FA is not enabled'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Generate new backup codes
    backup_codes = generate_backup_codes()
    hashed_codes = [hash_backup_code(code) for code in backup_codes]

    user.twofa_backup_codes = hashed_codes
    user.save()

    return Response({
        'message': 'Backup codes regenerated successfully',
        'backup_codes': backup_codes,
        'warning': 'Save these backup codes in a secure location. Old backup codes are no longer valid.'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_2fa_status(request):
    """
    Get current 2FA status for the authenticated user.
    """
    user = request.user

    return Response({
        'twofa_enabled': user.twofa_enabled,
        'backup_codes_remaining': len(user.twofa_backup_codes) if user.twofa_enabled else 0,
        'email': user.email
    })
