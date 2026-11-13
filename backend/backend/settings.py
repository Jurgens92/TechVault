"""
Django settings for TechVault project.
"""
import os
from pathlib import Path
from datetime import timedelta
from decouple import config, Csv

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Security Settings
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Encryption key for password/sensitive data encryption (Fernet)
# This MUST remain stable once set - changing it will make existing encrypted data unreadable.
# Defaults to SECRET_KEY for backwards compatibility, but should be set independently in production.
FIELD_ENCRYPTION_KEY = config('FIELD_ENCRYPTION_KEY', default=SECRET_KEY)

# Security: Fail if using insecure SECRET_KEY in production
if not DEBUG and SECRET_KEY == 'django-insecure-change-this-in-production':
    raise ValueError(
        "SECURITY ERROR: You must set a secure SECRET_KEY in production! "
        "Generate one with: python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
    )

# Production Security Settings
if not DEBUG:
    # HTTPS Security - only redirect to HTTPS if explicitly enabled
    # Self-hosted deployments may run on HTTP only (behind a firewall, etc.)
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # HTTPS-dependent settings - only enable when SSL is actually configured
    if SECURE_SSL_REDIRECT:
        # HSTS (HTTP Strict Transport Security)
        SECURE_HSTS_SECONDS = 31536000  # 1 year
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True

        # Cookie Security - secure cookies only work over HTTPS
        SESSION_COOKIE_SECURE = True
        CSRF_COOKIE_SECURE = True
    else:
        # No HTTPS - disable secure-only cookies so auth works over HTTP
        SESSION_COOKIE_SECURE = False
        CSRF_COOKIE_SECURE = False

    # Content Security
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True

# Always apply these security settings
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
# The CSRF cookie must be readable by the frontend so it can echo it back in the
# X-CSRFToken header (double-submit). It is not a secret; the auth tokens themselves
# live in HttpOnly cookies.
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third-party apps
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    # Required for BLACKLIST_AFTER_ROTATION and logout to actually revoke refresh tokens
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',  # OpenAPI Schema - Single Source of Truth for API
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth',
    'dj_rest_auth.registration',

    # Local apps
    'core',
    'users',
    'api',
    'reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    # Security: Additional security headers (CSP, Permissions-Policy, etc.)
    'backend.security_middleware.SecurityHeadersMiddleware',
    # Security: Enforce 2FA for all authenticated users
    'users.enforce_2fa_middleware.Enforce2FAMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# ------------------------------------------------------------------
# DATABASE CONFIGURATION
# ------------------------------------------------------------------

# Use SQLite when running locally (DEBUG=True or ENVIRONMENT=local/dev)
# Use PostgreSQL in production (ENVIRONMENT=production or DEBUG=False)
ENVIRONMENT = config("ENVIRONMENT", default="development")   # e.g. "development" or "production"

if ENVIRONMENT in ["development", "local", "dev"] or os.getenv("USE_SQLITE", "0") == "1":
    # SQLite for local development
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    # PostgreSQL for staging / production
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DB_NAME"),
            "USER": config("DB_USER"),
            "PASSWORD": config("DB_PASSWORD"),
            "HOST": config("DB_HOST", default="localhost"),
            "PORT": config("DB_PORT", default="5432"),
            # Recommended production settings
            "CONN_MAX_AGE": 60,
            "OPTIONS": {
                "sslmode": config("DB_SSLMODE", default="prefer"),
            },
            # Helps with connection issues in containers
            "DISABLE_SERVER_SIDE_CURSORS": True,
        }
    }
# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Sites Framework
SITE_ID = 1

# CORS Settings
# Check if CORS_ALLOW_ALL_ORIGINS is set (for self-hosted deployments)
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=False, cast=bool)

if not CORS_ALLOW_ALL_ORIGINS:
    # Use specific origins if CORS_ALLOW_ALL_ORIGINS is not enabled
    CORS_ALLOWED_ORIGINS = config(
        'CORS_ALLOWED_ORIGINS',
        default='http://localhost:5173,http://127.0.0.1:5173',
        cast=Csv()
    )

CORS_ALLOW_CREDENTIALS = True

# Security: Prevent insecure CORS wildcard with credentials in production
if not DEBUG and CORS_ALLOW_ALL_ORIGINS:
    raise ValueError(
        "SECURITY ERROR: CORS_ALLOW_ALL_ORIGINS must be False in production! "
        "Set CORS_ALLOWED_ORIGINS to your specific domain(s) instead."
    )

# CSRF Trusted Origins - required by Django 4+ for HTTPS
# Without this, all POST requests fail with CSRF errors when using HTTPS
_csrf_trusted = config('CSRF_TRUSTED_ORIGINS', default='', cast=str)
if isinstance(_csrf_trusted, str) and _csrf_trusted:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in _csrf_trusted.split(',') if origin.strip()]
elif not CORS_ALLOW_ALL_ORIGINS:
    # Cookie-authenticated requests are CSRF-checked, so a frontend served from a
    # different origin (e.g. the Vite dev server) must be trusted explicitly.
    CSRF_TRUSTED_ORIGINS = list(CORS_ALLOWED_ORIGINS)

# Client IP handling. When True, X-Forwarded-For is honoured only for requests that
# arrive from a private/loopback address (i.e. via the local reverse proxy).
TRUST_PROXY_HEADERS = config('TRUST_PROXY_HEADERS', default=True, cast=bool)

# Django admin (/admin/) authenticates with password only - it does not go through
# the 2FA or account-lockout flow. It is therefore disabled in production unless
# explicitly enabled.
ENABLE_DJANGO_ADMIN = config('ENABLE_DJANGO_ADMIN', default=DEBUG, cast=bool)

# Cache (used for rate limiting). The default in-memory cache is per-process, which
# means each gunicorn worker would keep its own throttle counters. Use a shared
# file-based cache in production so limits apply across workers.
if not DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': config('CACHE_DIR', default=str(BASE_DIR / '.cache')),
        }
    }

# REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # Authorization header first, then the HttpOnly auth cookie (CSRF-checked)
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',  # Anonymous users: 100 requests per hour
        'user': '1000/hour',  # Authenticated users: 1000 requests per hour
        'login': '5/minute',  # Login endpoint: 5 attempts per minute
        '2fa_verification': '10/minute',  # 2FA verification: 10 attempts per minute
    },
    # Number of trusted reverse proxies in front of the app (nginx). Used by DRF
    # throttling to pick the client address from X-Forwarded-For; without it the
    # whole header (client-controlled) is used as the throttle key.
    'NUM_PROXIES': config('NUM_PROXIES', default=1, cast=int),
    # OpenAPI Schema - Single Source of Truth for API documentation
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# DRF Spectacular Settings (OpenAPI Schema Generation)
# This is the Single Source of Truth for API documentation
# Frontend TypeScript types can be auto-generated from this schema
SPECTACULAR_SETTINGS = {
    'TITLE': 'TechVault API',
    'DESCRIPTION': 'Enterprise-grade IT Documentation Platform API - Single Source of Truth for IT infrastructure management',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
    'TAGS': [
        {'name': 'Authentication', 'description': 'User authentication and 2FA'},
        {'name': 'Organizations', 'description': 'Organization management'},
        {'name': 'Locations', 'description': 'Location management'},
        {'name': 'Contacts', 'description': 'Contact management'},
        {'name': 'Documentation', 'description': 'IT documentation and procedures'},
        {'name': 'Passwords', 'description': 'Secure password vault'},
        {'name': 'Configurations', 'description': 'System configurations'},
        {'name': 'Network Devices', 'description': 'Network infrastructure'},
        {'name': 'Servers', 'description': 'Server inventory'},
        {'name': 'Endpoints', 'description': 'Endpoint devices'},
        {'name': 'Peripherals', 'description': 'Peripheral devices'},
        {'name': 'Software', 'description': 'Software licenses'},
        {'name': 'Backups', 'description': 'Backup solutions'},
        {'name': 'VoIP', 'description': 'VoIP services'},
        {'name': 'Reports', 'description': 'Reporting and exports'},
        {'name': 'Meta', 'description': 'Metadata endpoints (choices, schema)'},
    ],
}

# Simple JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('ACCESS_TOKEN_LIFETIME_MINUTES', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('REFRESH_TOKEN_LIFETIME_DAYS', default=7, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# Django-allauth Settings
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'none'  # Don't require email verification for now
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_ADAPTER = 'allauth.account.adapter.DefaultAccountAdapter'

# dj-rest-auth Settings
REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': 'techvault-auth',
    'JWT_AUTH_REFRESH_COOKIE': 'techvault-refresh-token',
    # Security: Use HttpOnly cookies to prevent XSS token theft
    'JWT_AUTH_HTTPONLY': True,
    'JWT_AUTH_SECURE': not DEBUG and config('SECURE_SSL_REDIRECT', default=False, cast=bool),  # Secure cookies only when HTTPS is configured
    'JWT_AUTH_SAMESITE': 'Lax',  # Prevent CSRF while allowing same-site requests
    # Requests authenticated by cookie must pass Django's CSRF check
    'JWT_AUTH_COOKIE_USE_CSRF': True,
    # Changing your password requires the current one
    'OLD_PASSWORD_FIELD_ENABLED': True,
    'USER_DETAILS_SERIALIZER': 'users.serializers.UserSerializer',
    'LOGIN_SERIALIZER': 'users.serializers.LoginSerializer',
    'REGISTER_SERIALIZER': 'users.serializers.RegisterSerializer',
    'JWT_SERIALIZER': 'users.serializers.JWTSerializer',
}


# Email Backend (for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging Configuration
(BASE_DIR / 'logs').mkdir(exist_ok=True)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'security': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
