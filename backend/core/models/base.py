from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class SoftDeleteManager(models.Manager):
    """Manager to exclude soft-deleted records from default queryset."""

    def get_queryset(self):
        """Return only non-deleted records."""
        return super().get_queryset().filter(deleted_at__isnull=True)

    def deleted(self):
        """Return only soft-deleted records."""
        return super().get_queryset().filter(deleted_at__isnull=False)

    def with_deleted(self):
        """Return all records including soft-deleted ones."""
        return super().get_queryset()


class BaseModel(models.Model):
    """Abstract base model with common fields for all entities."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_deleted')

    # Default manager - excludes deleted records
    objects = SoftDeleteManager()
    # Manager to access all records including deleted
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, user=None):
        """Soft delete - mark as deleted instead of removing from database."""
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user
        self.save(update_fields=['deleted_at', 'deleted_by', 'updated_at'])

    def hard_delete(self, using=None, keep_parents=False):
        """Permanently delete from database."""
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """Restore a soft-deleted record."""
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=['deleted_at', 'deleted_by', 'updated_at'])

    @property
    def is_deleted(self):
        """Check if record is soft-deleted."""
        return self.deleted_at is not None
