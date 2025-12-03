"""
Rate limiting and throttling for authentication endpoints.
Implements brute force protection for login attempts.
"""
from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """
    Throttle for login endpoint to prevent brute force attacks.
    Allows 5 login attempts per minute per IP address.
    """
    scope = 'login'
    rate = '5/minute'


class TwoFAVerificationThrottle(AnonRateThrottle):
    """
    Throttle for 2FA verification to prevent brute force attacks on 2FA tokens.
    Allows 10 attempts per minute per IP address (slightly more lenient than login).
    """
    scope = '2fa_verification'
    rate = '10/minute'
