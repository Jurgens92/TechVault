from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication.
    """

    def create_user(self, email, password=None, first_name='', last_name='', **extra_fields):
        """Create and save a regular user with password validation."""
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)

        # Validate password strength before setting
        if password:
            try:
                validate_password(password, user)
            except ValidationError as e:
                raise ValueError(f"Password validation failed: {', '.join(e.messages)}")

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, first_name='', last_name='', **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(email, password, first_name, last_name, **extra_fields)


class User(AbstractUser):
    """
    Custom User model for TechVault.
    Uses email as the primary identifier instead of username.
    """
    email = models.EmailField(unique=True)
    username = None  # Remove username field

    # Two-Factor Authentication fields
    twofa_secret = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        help_text="TOTP secret key for 2FA"
    )
    twofa_enabled = models.BooleanField(
        default=False,
        help_text="Whether 2FA is enabled for this user"
    )
    twofa_backup_codes = models.JSONField(
        default=list,
        blank=True,
        help_text="Backup codes for 2FA recovery (hashed)"
    )

    # Account lockout fields for brute force protection
    failed_login_attempts = models.IntegerField(
        default=0,
        help_text="Number of consecutive failed login attempts"
    )
    locked_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Account is locked until this datetime"
    )
    last_failed_login = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of last failed login attempt"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def is_locked(self):
        """Check if the account is currently locked."""
        from django.utils import timezone
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False

    def record_failed_login(self):
        """Record a failed login attempt and lock account if threshold reached."""
        from django.utils import timezone
        from datetime import timedelta

        MAX_FAILED_ATTEMPTS = 5
        LOCKOUT_DURATION_MINUTES = 15

        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()

        if self.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            self.locked_until = timezone.now() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)

        self.save(update_fields=['failed_login_attempts', 'last_failed_login', 'locked_until'])

    def reset_failed_login_attempts(self):
        """Reset failed login attempts after successful login."""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.last_failed_login = None
        self.save(update_fields=['failed_login_attempts', 'locked_until', 'last_failed_login'])

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
