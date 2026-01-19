from django.db import models
from .base import BaseModel
from .organization import Organization, Location
from core.constants import NetworkDeviceType


class ConnectionType:
    """Connection type choices for internet connections."""
    FIBER = 'fiber'
    CABLE = 'cable'
    DSL = 'dsl'
    WIRELESS = 'wireless'
    SATELLITE = 'satellite'
    OTHER = 'other'

    CHOICES = [
        (FIBER, 'Fiber'),
        (CABLE, 'Cable'),
        (DSL, 'DSL'),
        (WIRELESS, '5G/Wireless'),
        (SATELLITE, 'Satellite'),
        (OTHER, 'Other'),
    ]
    DEFAULT = FIBER


class NetworkDevice(BaseModel):
    """Network infrastructure devices like firewalls, routers, switches, and WiFi."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='network_devices', db_index=True)
    name = models.CharField(max_length=255)
    device_type = models.CharField(
        max_length=50,
        choices=NetworkDeviceType.CHOICES,
        default=NetworkDeviceType.DEFAULT
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
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='network_devices', db_index=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['organization', 'device_type', 'name']
        db_table = 'network_devices'

    def __str__(self):
        return f"{self.name} ({self.get_device_type_display()})"


class InternetConnection(BaseModel):
    """Internet/ISP connections for network devices (supports multiple connections per device)."""
    network_device = models.ForeignKey(
        NetworkDevice,
        on_delete=models.CASCADE,
        related_name='internet_connections',
        db_index=True
    )
    provider_name = models.CharField(max_length=255)
    connection_type = models.CharField(
        max_length=50,
        choices=ConnectionType.CHOICES,
        default=ConnectionType.DEFAULT
    )
    download_speed = models.PositiveIntegerField(help_text='Download speed in Mbps')
    upload_speed = models.PositiveIntegerField(help_text='Upload speed in Mbps')
    is_primary = models.BooleanField(default=True, help_text='Primary connection for failover')
    account_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['network_device', '-is_primary', 'provider_name']
        db_table = 'internet_connections'

    def __str__(self):
        return f"{self.provider_name} ({self.download_speed}/{self.upload_speed} Mbps)"

    @property
    def speed_display(self):
        """Return formatted speed string."""
        return f"{self.download_speed}/{self.upload_speed} Mbps"
