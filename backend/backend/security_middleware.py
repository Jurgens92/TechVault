"""
Security middleware for TechVault.
Adds Content Security Policy and other security headers.
"""
from django.conf import settings


class SecurityHeadersMiddleware:
    """
    Middleware to add security headers to all responses.
    Implements defense-in-depth with multiple security headers.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Content Security Policy
        # Restricts sources of content to prevent XSS and data injection attacks
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline'",  # Allow inline scripts for React
            "style-src 'self' 'unsafe-inline'",  # Allow inline styles
            "img-src 'self' data: https:",  # Allow images from self, data URIs, and HTTPS
            "font-src 'self' data:",  # Allow fonts from self and data URIs
            "connect-src 'self'",  # Only allow connections to same origin
            "frame-ancestors 'none'",  # Prevent framing (clickjacking protection)
            "base-uri 'self'",  # Restrict base tag sources
            "form-action 'self'",  # Restrict form submission targets
            "object-src 'none'",  # Disable plugins
        ]

        # Only add CSP in production or when explicitly enabled
        if not settings.DEBUG:
            response['Content-Security-Policy'] = "; ".join(csp_directives)

        # Permissions-Policy (formerly Feature-Policy)
        # Restricts access to browser features
        permissions = [
            "accelerometer=()",
            "camera=()",
            "geolocation=()",
            "gyroscope=()",
            "magnetometer=()",
            "microphone=()",
            "payment=()",
            "usb=()",
        ]
        response['Permissions-Policy'] = ", ".join(permissions)

        # Cross-Origin headers for additional isolation
        response['Cross-Origin-Embedder-Policy'] = 'require-corp'
        response['Cross-Origin-Opener-Policy'] = 'same-origin'
        response['Cross-Origin-Resource-Policy'] = 'same-origin'

        # Cache control for sensitive pages
        if request.path.startswith('/api/'):
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
            response['Pragma'] = 'no-cache'

        return response
