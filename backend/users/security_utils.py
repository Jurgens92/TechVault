"""
Security utilities for authentication and logging.
"""
import logging
from django.contrib.auth.hashers import check_password

logger = logging.getLogger('security')


def log_authentication_event(event_type, email, request, success=True, details=''):
    """
    Log authentication events for security monitoring and audit trail.

    Args:
        event_type: Type of event (login, 2fa, logout, etc.)
        email: User's email address
        request: Django request object
        success: Whether the event was successful
        details: Additional details about the event
    """
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    status_str = 'SUCCESS' if success else 'FAILED'

    log_message = (
        f"{event_type.upper()} {status_str} | "
        f"Email: {email} | "
        f"IP: {ip_address} | "
        f"User-Agent: {user_agent[:100]}"
    )

    if details:
        log_message += f" | Details: {details}"

    if success:
        logger.info(log_message)
    else:
        logger.warning(log_message)


def get_client_ip(request):
    """
    Get the client's IP address from the request.
    Handles proxy headers (X-Forwarded-For) correctly.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Take the first IP in the chain
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'Unknown')
    return ip


def constant_time_check_user(email, password):
    """
    Perform user authentication with constant-time comparison
    to prevent timing attacks that reveal valid email addresses.

    Args:
        email: User's email address
        password: Provided password

    Returns:
        tuple: (user_object or None, is_authenticated bool)
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        user = User.objects.get(email=email)
        is_valid = user.check_password(password) and user.is_active
    except User.DoesNotExist:
        # Perform dummy hash operation to maintain constant time
        # This prevents timing attacks that detect valid vs invalid emails
        check_password(password, 'pbkdf2_sha256$600000$dummy$invalidhash')
        user = None
        is_valid = False

    return user, is_valid
