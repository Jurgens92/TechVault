from django.db import models
from .base import BaseModel
from .organization import Organization, Location


class Backup(BaseModel):
    """Backup solutions for servers, cloud services, and endpoints."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='backups')
    name = models.CharField(max_length=255, help_text='Backup solution name or identifier')
    backup_type = models.CharField(
        max_length=50,
        choices=[
            ('server', 'Server Backup'),
            ('microsoft365', 'Microsoft 365 Backup'),
            ('cloud', 'Cloud Backup'),
            ('endpoint', 'Endpoint Backup'),
            ('database', 'Database Backup'),
            ('nas', 'NAS Backup'),
            ('other', 'Other'),
        ],
        default='other'
    )

    # Backup details
    vendor = models.CharField(max_length=255, blank=True, help_text='Backup solution vendor')
    frequency = models.CharField(max_length=100, blank=True, help_text='e.g., Daily, Hourly, Weekly')
    retention_period = models.CharField(max_length=100, blank=True, help_text='e.g., 30 days, 1 year')
    storage_location = models.CharField(max_length=255, blank=True, help_text='Where backups are stored')
    storage_capacity = models.CharField(max_length=100, blank=True, help_text='e.g., 500GB, 2TB')

    # Target information
    target_systems = models.TextField(blank=True, help_text='Systems or data being backed up')

    # Status and monitoring
    last_backup_date = models.DateTimeField(null=True, blank=True, help_text='Last successful backup')
    next_backup_date = models.DateTimeField(null=True, blank=True, help_text='Next scheduled backup')
    backup_status = models.CharField(
        max_length=50,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('failed', 'Failed'),
            ('warning', 'Warning'),
        ],
        default='active'
    )

    # Other details
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='backups')
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['organization', 'backup_type', 'name']
        db_table = 'backups'

    def __str__(self):
        return f"{self.name} ({self.get_backup_type_display()})"
