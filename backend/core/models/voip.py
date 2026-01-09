from django.db import models
from .base import BaseModel
from .organization import Organization, Contact
from core.constants import VoIPType, LicenseType


class VoIP(BaseModel):
    """VoIP licenses and services assigned to users."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='voip')
    name = models.CharField(max_length=255, help_text='VoIP service name or product')
    voip_type = models.CharField(
        max_length=50,
        choices=VoIPType.CHOICES,
        default=VoIPType.DEFAULT
    )

    # License information
    license_key = models.CharField(max_length=255, blank=True, help_text='License code or account ID')
    version = models.CharField(max_length=100, blank=True, help_text='e.g., Business, Enterprise, Pro')
    license_type = models.CharField(
        max_length=50,
        choices=LicenseType.CHOICES,
        default=LicenseType.SUBSCRIPTION  # VoIP typically defaults to subscription
    )

    # License dates
    purchase_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True, help_text='License expiration date')

    # Additional details
    vendor = models.CharField(max_length=255, blank=True, help_text='VoIP vendor or service provider')
    quantity = models.IntegerField(default=1, help_text='Number of licenses/extensions')

    # VoIP-specific fields
    phone_numbers = models.TextField(blank=True, help_text='Associated phone numbers (comma-separated)')
    extensions = models.TextField(blank=True, help_text='Extension numbers (comma-separated)')

    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['organization', 'voip_type', 'name']
        db_table = 'voip'

    def __str__(self):
        return f"{self.name} ({self.get_voip_type_display()})"

    @property
    def assigned_count(self):
        """Return the number of users this VoIP service is assigned to."""
        return self.voip_assignments.count()

    @property
    def available_licenses(self):
        """Return the number of available licenses."""
        return self.quantity - self.assigned_count


class VoIPAssignment(BaseModel):
    """Assignment of VoIP licenses to contacts."""
    voip = models.ForeignKey(VoIP, on_delete=models.CASCADE, related_name='voip_assignments')
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='voip_assignments')
    extension = models.CharField(max_length=50, blank=True, help_text='Assigned extension number')
    phone_number = models.CharField(max_length=50, blank=True, help_text='Assigned phone number')

    class Meta:
        db_table = 'voip_assignments'
        unique_together = ('voip', 'contact')

    def __str__(self):
        return f"{self.voip.name} -> {self.contact.full_name}"
