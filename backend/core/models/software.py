from django.db import models
from .base import BaseModel
from .organization import Organization, Contact
from core.constants import SoftwareType, LicenseType


class Software(BaseModel):
    """Software licenses and applications assigned to users."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='software', db_index=True)
    name = models.CharField(max_length=255, help_text='Software name or product')
    software_type = models.CharField(
        max_length=50,
        choices=SoftwareType.CHOICES,
        default=SoftwareType.DEFAULT
    )

    # License information
    license_key = models.CharField(max_length=255, blank=True, help_text='Product key or license code')
    version = models.CharField(max_length=100, blank=True, help_text='e.g., 2024, Pro, Standard')
    license_type = models.CharField(
        max_length=50,
        choices=LicenseType.CHOICES,
        default=LicenseType.DEFAULT
    )

    # License dates
    purchase_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True, help_text='License expiration date')

    # Additional details
    vendor = models.CharField(max_length=255, blank=True, help_text='Software vendor or publisher')
    quantity = models.IntegerField(default=1, help_text='Number of licenses')

    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['organization', 'software_type', 'name']
        db_table = 'software'

    def __str__(self):
        return f"{self.name} ({self.get_software_type_display()})"

    @property
    def assigned_count(self):
        """Return the number of users this software is assigned to."""
        return self.software_assignments.count()

    @property
    def available_licenses(self):
        """Return the number of available licenses."""
        return self.quantity - self.assigned_count


class SoftwareAssignment(BaseModel):
    """Assignment of software licenses to contacts."""
    software = models.ForeignKey(Software, on_delete=models.CASCADE, related_name='software_assignments', db_index=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='software_assignments', db_index=True)

    class Meta:
        db_table = 'software_assignments'
        unique_together = ('software', 'contact')

    def __str__(self):
        return f"{self.software.name} -> {self.contact.full_name}"
