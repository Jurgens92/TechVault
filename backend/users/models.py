from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication.
    """

    def create_user(self, email, password=None, first_name='', last_name='', **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
