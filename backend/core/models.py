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


class Organization(BaseModel):
    """Organizations for grouping IT infrastructure."""
    name = models.CharField(max_length=255, unique=True)
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

    def __str__(self):
        return self.name


class Location(BaseModel):
    """Physical locations within an organization."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='locations')
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
        unique_together = ('organization', 'name')

    def __str__(self):
        return f"{self.name} - {self.organization.name}"


class Contact(BaseModel):
    """Contacts for organizations and locations."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='contacts')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='contacts')
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
        unique_together = ('organization', 'email')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


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


class PasswordEntry(BaseModel):
    """Secure password vault entries."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='password_entries')
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, blank=True)
    password = models.TextField()  # Should be encrypted in production
    url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    category = models.CharField(
        max_length=50,
        choices=[
            ('account', 'Account'),
            ('service', 'Service'),
            ('device', 'Device'),
            ('other', 'Other'),
        ],
        default='other'
    )
    is_encrypted = models.BooleanField(default=False)

    class Meta:
        ordering = ['organization', 'name']
        db_table = 'password_entries'

    def __str__(self):
        return self.name


class Configuration(BaseModel):
    """System and service configurations."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='configurations')
    name = models.CharField(max_length=255)
    config_type = models.CharField(
        max_length=50,
        choices=[
            ('network', 'Network'),
            ('server', 'Server'),
            ('application', 'Application'),
            ('security', 'Security'),
            ('backup', 'Backup'),
            ('other', 'Other'),
        ],
        default='other'
    )
    content = models.TextField(help_text='Configuration details, code, or settings')
    description = models.TextField(blank=True)
    version = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['organization', 'config_type', 'name']
        db_table = 'configurations'
        unique_together = ('organization', 'name')

    def __str__(self):
        return self.name


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
