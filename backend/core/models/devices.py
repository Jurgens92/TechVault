from django.db import models
from .base import BaseModel
from .organization import Organization, Location, Contact


class EndpointUser(BaseModel):
    """User endpoints like desktops and laptops."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='endpoint_users')
    name = models.CharField(max_length=255, help_text='Device name or identifier')
    device_type = models.CharField(
        max_length=50,
        choices=[
            ('desktop', 'Desktop'),
            ('laptop', 'Laptop'),
            ('workstation', 'Workstation'),
            ('other', 'Other'),
        ],
        default='desktop'
    )

    # User assignment
    assigned_to = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_devices')

    # Hardware specifications
    manufacturer = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=True)
    cpu = models.CharField(max_length=255, blank=True, help_text='Processor details')
    ram = models.CharField(max_length=100, blank=True, help_text='e.g., 16GB DDR4')
    storage = models.CharField(max_length=255, blank=True, help_text='e.g., 512GB SSD')
    gpu = models.CharField(max_length=255, blank=True, help_text='Graphics card details')

    # Software
    operating_system = models.CharField(max_length=255, blank=True, help_text='e.g., Windows 11 Pro')
    software_installed = models.TextField(blank=True, help_text='Comma-separated list of installed software')

    # Network
    ip_address = models.CharField(max_length=50, blank=True)
    mac_address = models.CharField(max_length=50, blank=True)
    hostname = models.CharField(max_length=255, blank=True)

    # Other details
    serial_number = models.CharField(max_length=255, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='endpoint_users')
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['organization', 'device_type', 'name']
        db_table = 'endpoint_users'

    def __str__(self):
        return f"{self.name} ({self.get_device_type_display()})"


class Server(BaseModel):
    """Server infrastructure."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='servers')
    name = models.CharField(max_length=255)
    server_type = models.CharField(
        max_length=50,
        choices=[
            ('physical', 'Physical Server'),
            ('virtual', 'Virtual Machine'),
            ('cloud', 'Cloud Instance'),
            ('container', 'Container'),
            ('other', 'Other'),
        ],
        default='physical'
    )

    # Server role/purpose
    role = models.CharField(max_length=255, blank=True, help_text='e.g., Web Server, Database, File Server')

    # Hardware specifications
    manufacturer = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=True)
    cpu = models.CharField(max_length=255, blank=True, help_text='Processor details')
    ram = models.CharField(max_length=100, blank=True, help_text='e.g., 64GB DDR4')
    storage = models.CharField(max_length=255, blank=True, help_text='e.g., 2TB SSD RAID 10')

    # Software
    operating_system = models.CharField(max_length=255, blank=True, help_text='e.g., Ubuntu 22.04 LTS')
    software_installed = models.TextField(blank=True, help_text='Comma-separated list of installed software')

    # Network
    ip_address = models.CharField(max_length=50, blank=True)
    mac_address = models.CharField(max_length=50, blank=True)
    hostname = models.CharField(max_length=255, blank=True)

    # Other details
    serial_number = models.CharField(max_length=255, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='servers')
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['organization', 'server_type', 'name']
        db_table = 'servers'

    def __str__(self):
        return f"{self.name} ({self.get_server_type_display()})"


class Peripheral(BaseModel):
    """Peripheral devices like printers, scanners, etc."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='peripherals')
    name = models.CharField(max_length=255)
    device_type = models.CharField(
        max_length=50,
        choices=[
            ('printer', 'Printer'),
            ('scanner', 'Scanner'),
            ('multifunction', 'Multifunction Printer'),
            ('ups', 'UPS'),
            ('nas', 'NAS'),
            ('other', 'Other'),
        ],
        default='printer'
    )

    # Device details
    manufacturer = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=True)
    ip_address = models.CharField(max_length=50, blank=True)
    mac_address = models.CharField(max_length=50, blank=True)
    serial_number = models.CharField(max_length=255, blank=True)

    # Other details
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='peripherals')
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['organization', 'device_type', 'name']
        db_table = 'peripherals'

    def __str__(self):
        return f"{self.name} ({self.get_device_type_display()})"
