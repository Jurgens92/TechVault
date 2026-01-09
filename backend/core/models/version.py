"""
Unified Version History System - Single Source of Truth for all entity versions.

This module provides a generic versioning system that works with any model,
eliminating the need for separate version tables per entity type.

Usage:
    from core.models.version import EntityVersion

    # Create a version when saving
    EntityVersion.create_version(instance, user, change_note="Updated title")

    # Get version history
    versions = EntityVersion.get_versions(instance)

    # Restore a version
    EntityVersion.restore_version(instance, version_number, user)
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
import uuid
import json

User = get_user_model()


class EntityVersionManager(models.Manager):
    """Manager for EntityVersion with helper methods."""

    def for_instance(self, instance):
        """Get all versions for a specific instance."""
        content_type = ContentType.objects.get_for_model(instance)
        return self.filter(
            content_type=content_type,
            object_id=str(instance.pk)
        ).order_by('-version_number')

    def get_latest_version_number(self, instance):
        """Get the latest version number for an instance."""
        content_type = ContentType.objects.get_for_model(instance)
        latest = self.filter(
            content_type=content_type,
            object_id=str(instance.pk)
        ).order_by('-version_number').first()
        return latest.version_number if latest else 0


class EntityVersion(models.Model):
    """
    Unified version history for all versionable entities.

    Uses Django's ContentType framework to create a single version table
    that can store snapshots of any model. This is the Single Source of Truth
    for all version history, replacing the previous per-entity version tables.

    Advantages over per-entity version tables:
    - Single schema definition for versioning logic
    - New entities automatically support versioning
    - Consistent API across all entity types
    - Reduced database complexity
    - Easier maintenance and migrations
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Generic relation to any model
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text='The type of entity being versioned'
    )
    object_id = models.CharField(
        max_length=36,
        help_text='UUID of the entity being versioned'
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    # Version metadata
    version_number = models.IntegerField(
        help_text='Sequential version number for this entity'
    )
    change_note = models.TextField(
        blank=True,
        help_text='Optional description of what changed in this version'
    )

    # Snapshot of entity state (stored as JSON)
    snapshot = models.JSONField(
        encoder=DjangoJSONEncoder,
        help_text='Complete serialized state of the entity at this version'
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='entity_versions_created'
    )

    objects = EntityVersionManager()

    class Meta:
        db_table = 'entity_versions'
        ordering = ['-version_number']
        unique_together = ('content_type', 'object_id', 'version_number')
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.content_type.model} {self.object_id} - v{self.version_number}"

    @classmethod
    def create_version(cls, instance, user=None, change_note='', serializer_class=None):
        """
        Create a new version snapshot for an entity.

        Args:
            instance: The model instance to version
            user: The user creating this version (optional)
            change_note: Description of changes (optional)
            serializer_class: Optional DRF serializer to use for snapshot.
                             If not provided, uses model_to_dict.

        Returns:
            EntityVersion: The newly created version
        """
        content_type = ContentType.objects.get_for_model(instance)

        # Get the next version number
        version_number = cls.objects.get_latest_version_number(instance) + 1

        # Create snapshot
        if serializer_class:
            # Use provided serializer for consistent API representation
            snapshot = serializer_class(instance).data
        else:
            # Use simple dict conversion
            snapshot = cls._instance_to_dict(instance)

        return cls.objects.create(
            content_type=content_type,
            object_id=str(instance.pk),
            version_number=version_number,
            snapshot=snapshot,
            change_note=change_note,
            created_by=user
        )

    @classmethod
    def get_versions(cls, instance):
        """
        Get all versions for an entity, ordered by version number descending.

        Args:
            instance: The model instance

        Returns:
            QuerySet: All versions for this instance
        """
        return cls.objects.for_instance(instance)

    @classmethod
    def get_version(cls, instance, version_number):
        """
        Get a specific version of an entity.

        Args:
            instance: The model instance
            version_number: The version number to retrieve

        Returns:
            EntityVersion: The requested version, or None if not found
        """
        content_type = ContentType.objects.get_for_model(instance)
        return cls.objects.filter(
            content_type=content_type,
            object_id=str(instance.pk),
            version_number=version_number
        ).first()

    @classmethod
    def restore_version(cls, instance, version_number, user=None, create_new_version=True):
        """
        Restore an entity to a previous version.

        Args:
            instance: The model instance to restore
            version_number: The version number to restore to
            user: The user performing the restore (optional)
            create_new_version: Whether to create a new version before restoring

        Returns:
            tuple: (restored_instance, new_version or None)
        """
        version = cls.get_version(instance, version_number)
        if not version:
            raise ValueError(f"Version {version_number} not found")

        # Create a new version of current state before restoring (optional)
        new_version = None
        if create_new_version:
            new_version = cls.create_version(
                instance,
                user=user,
                change_note=f"State before restoring to version {version_number}"
            )

        # Restore fields from snapshot
        snapshot = version.snapshot
        for field_name, value in snapshot.items():
            # Skip non-editable and relation fields
            if hasattr(instance, field_name) and field_name not in ['id', 'pk', 'created_at', 'created_by']:
                try:
                    setattr(instance, field_name, value)
                except (AttributeError, TypeError):
                    # Skip fields that can't be set (relations, computed properties)
                    pass

        instance.save()

        # Create a version for the restored state
        cls.create_version(
            instance,
            user=user,
            change_note=f"Restored from version {version_number}"
        )

        return instance, new_version

    @staticmethod
    def _instance_to_dict(instance):
        """
        Convert a model instance to a dictionary.

        This is a simple conversion that captures field values.
        For more complex serialization, use a DRF serializer.
        """
        from django.forms.models import model_to_dict

        # Get basic fields
        data = model_to_dict(instance)

        # Convert UUIDs to strings
        for key, value in data.items():
            if isinstance(value, uuid.UUID):
                data[key] = str(value)

        return data


# Fields that should be excluded when creating version snapshots
VERSION_EXCLUDE_FIELDS = [
    'id', 'pk', 'created_at', 'created_by', 'updated_at',
    'deleted_at', 'deleted_by', 'versions'
]
