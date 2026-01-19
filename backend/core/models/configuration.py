from django.db import models
from django.contrib.auth import get_user_model
import uuid
from .base import BaseModel
from .organization import Organization
from core.constants import ConfigurationType

User = get_user_model()


class Configuration(BaseModel):
    """System and service configurations."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='configurations', db_index=True)
    name = models.CharField(max_length=255)
    config_type = models.CharField(
        max_length=50,
        choices=ConfigurationType.CHOICES,
        default=ConfigurationType.DEFAULT
    )
    content = models.TextField(help_text='Configuration details, code, or settings')
    description = models.TextField(blank=True)
    version = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['organization', 'config_type', 'name']
        db_table = 'configurations'
        unique_together = ('organization', 'name')

    def __str__(self):
        return self.name


class ConfigurationVersion(models.Model):
    """Version history for Configuration entries."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    configuration = models.ForeignKey(Configuration, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()

    # Snapshot of Configuration fields
    name = models.CharField(max_length=255)
    config_type = models.CharField(max_length=50)
    content = models.TextField()
    description = models.TextField(blank=True)
    version = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    # Metadata
    change_note = models.TextField(blank=True, help_text='Optional description of what changed in this version')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='configuration_versions_created')

    class Meta:
        ordering = ['-version_number']
        db_table = 'configuration_versions'
        unique_together = ('configuration', 'version_number')

    def __str__(self):
        return f"{self.configuration.name} - v{self.version_number}"
