from django.db import models
from django.contrib.auth import get_user_model
import uuid
from .base import BaseModel
from .organization import Organization

User = get_user_model()


class Documentation(BaseModel):
    """Documentation for IT infrastructure, configurations, and procedures."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='documentations')
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(
        max_length=50,
        choices=[
            ('procedure', 'Procedure'),
            ('configuration', 'Configuration'),
            ('guide', 'Guide'),
            ('troubleshooting', 'Troubleshooting'),
            ('policy', 'Policy'),
            ('other', 'Other'),
        ],
        default='other'
    )
    tags = models.CharField(max_length=500, blank=True, help_text='Comma-separated tags')
    is_published = models.BooleanField(default=False)
    version = models.IntegerField(default=1)

    class Meta:
        ordering = ['-created_at']
        db_table = 'documentations'

    def __str__(self):
        return self.title


class DocumentationVersion(models.Model):
    """Version history for Documentation entries."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    documentation = models.ForeignKey(Documentation, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()

    # Snapshot of Documentation fields
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=50)
    tags = models.CharField(max_length=500, blank=True)
    is_published = models.BooleanField(default=False)

    # Metadata
    change_note = models.TextField(blank=True, help_text='Optional description of what changed in this version')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='documentation_versions_created')

    class Meta:
        ordering = ['-version_number']
        db_table = 'documentation_versions'
        unique_together = ('documentation', 'version_number')

    def __str__(self):
        return f"{self.documentation.title} - v{self.version_number}"
