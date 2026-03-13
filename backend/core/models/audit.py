from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class AuditLog(models.Model):
    """Tracks all user actions across the application for admin visibility."""

    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('restore', 'Restore'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)
    entity_type = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Model name, e.g. 'Organization', 'Documentation'",
    )
    entity_id = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Primary key of the affected object",
    )
    entity_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Human-readable name/title of the affected object",
    )
    organization_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Organization the entity belongs to, if applicable",
    )
    details = models.TextField(
        blank=True,
        default='',
        help_text="Additional details about the action",
    )
    changes = models.JSONField(
        null=True,
        blank=True,
        help_text="Structured change data: field-level diffs for updates, field values for creates/deletes",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'audit_log'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'action']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['entity_type', '-timestamp']),
        ]

    def __str__(self):
        user_display = self.user.full_name if self.user else 'System'
        return f"{user_display} {self.action}d {self.entity_type} '{self.entity_name}'"

    @classmethod
    def log(cls, user, action, entity_type, entity_id='', entity_name='',
            organization_name='', details='', changes=None, ip_address=None):
        """Create an audit log entry."""
        return cls.objects.create(
            user=user,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id),
            entity_name=str(entity_name),
            organization_name=str(organization_name),
            details=details,
            changes=changes,
            ip_address=ip_address,
        )
