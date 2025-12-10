from django.db import models
from .base import BaseModel
from .organization import Organization, Location


class NetworkDevice(BaseModel):
    """Network infrastructure devices like firewalls, routers, switches, and WiFi."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='network_devices')
    name = models.CharField(max_length=255)
    device_type = models.CharField(
        max_length=50,
        choices=[
            ('firewall', 'Firewall'),
            ('router', 'Router'),
            ('firewall_router', 'Firewall/Router'),
            ('switch', 'Switch'),
            ('wifi', 'WiFi Access Point'),
            ('other', 'Other'),
        ],
        default='other'
    )
    # Internet connection details (for firewall/router)
    internet_provider = models.CharField(max_length=255, blank=True)
    internet_speed = models.CharField(max_length=100, blank=True, help_text='e.g., 100/100 Mbps')

    # Device details
    manufacturer = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=True)
    ip_address = models.CharField(max_length=50, blank=True)
    mac_address = models.CharField(max_length=50, blank=True)
    serial_number = models.CharField(max_length=255, blank=True)

    # Configuration
    firmware_version = models.CharField(max_length=100, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='network_devices')
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['organization', 'device_type', 'name']
        db_table = 'network_devices'

    def __str__(self):
        return f"{self.name} ({self.get_device_type_display()})"
