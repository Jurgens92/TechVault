from django.db import models
from django.contrib.auth import get_user_model
import uuid
from .base import BaseModel
from .organization import Organization

User = get_user_model()


class PasswordEntry(BaseModel):
    """Secure password vault entries."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='password_entries')
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, blank=True)
    password = models.TextField()  # Should be encrypted in production
    url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    category = models.CharField(
        max_length=50,
        choices=[
            ('account', 'Account'),
            ('service', 'Service'),
            ('device', 'Device'),
            ('other', 'Other'),
        ],
        default='other'
    )
    is_encrypted = models.BooleanField(default=False)

    class Meta:
        ordering = ['organization', 'name']
        db_table = 'password_entries'

    def __str__(self):
        return self.name


class PasswordEntryVersion(models.Model):
    """Version history for PasswordEntry entries."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    password_entry = models.ForeignKey(PasswordEntry, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()

    # Snapshot of PasswordEntry fields
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, blank=True)
    password = models.TextField()
    url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    category = models.CharField(max_length=50)
    is_encrypted = models.BooleanField(default=False)

    # Metadata
    change_note = models.TextField(blank=True, help_text='Optional description of what changed in this version')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='password_versions_created')

    class Meta:
        ordering = ['-version_number']
        db_table = 'password_entry_versions'
        unique_together = ('password_entry', 'version_number')

    def __str__(self):
        return f"{self.password_entry.name} - v{self.version_number}"
