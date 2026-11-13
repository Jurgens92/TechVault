from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from .base import BaseModel

# Uniqueness only applies to live (non soft-deleted) rows, so a deleted record
# never blocks re-creating something with the same name.
NOT_DELETED = Q(deleted_at__isnull=True)


class Organization(BaseModel):
    """Organizations for grouping IT infrastructure."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state_province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        db_table = 'organizations'
        constraints = [
            models.UniqueConstraint(fields=['name'], condition=NOT_DELETED, name='uniq_active_organization_name'),
        ]

    def __str__(self):
        return self.name

    def _owned_models(self):
        """All soft-deletable models that belong to an organization via an 'organization' FK."""
        models_ = []
        for rel in self._meta.related_objects:
            model = rel.related_model
            if (
                rel.field.name == 'organization'
                and issubclass(model, BaseModel)
                and model.__name__ != 'OrganizationMember'
            ):
                models_.append(model)
        return models_

    @transaction.atomic
    def delete(self, using=None, keep_parents=False, user=None):
        """
        Soft delete the organization together with everything it owns.
        Children get the same deleted_at timestamp so restore() can bring back
        exactly the records that were removed by this cascade.
        """
        now = timezone.now()
        self.deleted_at = now
        if user:
            self.deleted_by = user
        self.save(update_fields=['deleted_at', 'deleted_by', 'updated_at'])
        for model in self._owned_models():
            model.objects.filter(organization=self).update(deleted_at=now, deleted_by=user)

    @transaction.atomic
    def restore(self):
        """Restore the organization and the children that were deleted along with it."""
        cascade_timestamp = self.deleted_at
        super().restore()
        if cascade_timestamp is not None:
            for model in self._owned_models():
                model.all_objects.filter(organization=self, deleted_at=cascade_timestamp).update(
                    deleted_at=None, deleted_by=None
                )


class Location(BaseModel):
    """Physical locations within an organization."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='locations', db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['organization', 'name']
        db_table = 'locations'
        constraints = [
            models.UniqueConstraint(fields=['organization', 'name'], condition=NOT_DELETED, name='uniq_active_location_name'),
        ]

    def __str__(self):
        return f"{self.name} - {self.organization.name}"


class Contact(BaseModel):
    """Contacts for organizations and locations."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='contacts', db_index=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='contacts', db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['organization', 'last_name', 'first_name']
        db_table = 'contacts'
        constraints = [
            models.UniqueConstraint(fields=['organization', 'email'], condition=NOT_DELETED, name='uniq_active_contact_email'),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
