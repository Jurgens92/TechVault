"""
Centralized constants module - Single Source of Truth for all choices/enums.

This module defines all choice constants used across the application.
Frontend should fetch these via the /api/meta/choices/ endpoint to ensure
consistency between frontend and backend.

Usage in models:
    from core.constants import DocumentationCategory
    category = models.CharField(choices=DocumentationCategory.CHOICES, ...)

Usage in frontend:
    Fetch from /api/meta/choices/ and cache in context/store.
"""


class BaseChoices:
    """Base class for choice definitions with utility methods."""

    CHOICES = []  # Override in subclasses

    @classmethod
    def get_values(cls):
        """Return list of valid values."""
        return [choice[0] for choice in cls.CHOICES]

    @classmethod
    def get_display(cls, value):
        """Get display label for a value."""
        for val, display in cls.CHOICES:
            if val == value:
                return display
        return value

    @classmethod
    def is_valid(cls, value):
        """Check if value is valid."""
        return value in cls.get_values()

    @classmethod
    def to_dict_list(cls):
        """Return choices as list of dicts for API response."""
        return [{'value': val, 'label': display} for val, display in cls.CHOICES]


# =============================================================================
# Documentation Choices
# =============================================================================

class DocumentationCategory(BaseChoices):
    """Categories for documentation entries."""
    PROCEDURE = 'procedure'
    CONFIGURATION = 'configuration'
    GUIDE = 'guide'
    TROUBLESHOOTING = 'troubleshooting'
    POLICY = 'policy'
    OTHER = 'other'

    CHOICES = [
        (PROCEDURE, 'Procedure'),
        (CONFIGURATION, 'Configuration'),
        (GUIDE, 'Guide'),
        (TROUBLESHOOTING, 'Troubleshooting'),
        (POLICY, 'Policy'),
        (OTHER, 'Other'),
    ]

    DEFAULT = OTHER


# =============================================================================
# Password Entry Choices
# =============================================================================

class PasswordCategory(BaseChoices):
    """Categories for password entries."""
    ACCOUNT = 'account'
    SERVICE = 'service'
    DEVICE = 'device'
    OTHER = 'other'

    CHOICES = [
        (ACCOUNT, 'Account'),
        (SERVICE, 'Service'),
        (DEVICE, 'Device'),
        (OTHER, 'Other'),
    ]

    DEFAULT = OTHER


# =============================================================================
# Configuration Choices
# =============================================================================

class ConfigurationType(BaseChoices):
    """Types of system configurations."""
    NETWORK = 'network'
    SERVER = 'server'
    APPLICATION = 'application'
    SECURITY = 'security'
    BACKUP = 'backup'
    OTHER = 'other'

    CHOICES = [
        (NETWORK, 'Network'),
        (SERVER, 'Server'),
        (APPLICATION, 'Application'),
        (SECURITY, 'Security'),
        (BACKUP, 'Backup'),
        (OTHER, 'Other'),
    ]

    DEFAULT = OTHER


# =============================================================================
# Network Device Choices
# =============================================================================

class NetworkDeviceType(BaseChoices):
    """Types of network devices."""
    FIREWALL = 'firewall'
    ROUTER = 'router'
    FIREWALL_ROUTER = 'firewall_router'
    SWITCH = 'switch'
    WIFI = 'wifi'
    OTHER = 'other'

    CHOICES = [
        (FIREWALL, 'Firewall'),
        (ROUTER, 'Router'),
        (FIREWALL_ROUTER, 'Firewall/Router'),
        (SWITCH, 'Switch'),
        (WIFI, 'WiFi Access Point'),
        (OTHER, 'Other'),
    ]

    DEFAULT = OTHER


# =============================================================================
# Endpoint/Device Choices
# =============================================================================

class EndpointDeviceType(BaseChoices):
    """Types of endpoint devices (desktops, laptops, etc.)."""
    DESKTOP = 'desktop'
    LAPTOP = 'laptop'
    WORKSTATION = 'workstation'
    OTHER = 'other'

    CHOICES = [
        (DESKTOP, 'Desktop'),
        (LAPTOP, 'Laptop'),
        (WORKSTATION, 'Workstation'),
        (OTHER, 'Other'),
    ]

    DEFAULT = DESKTOP


class ServerType(BaseChoices):
    """Types of servers."""
    PHYSICAL = 'physical'
    VIRTUAL = 'virtual'
    CLOUD = 'cloud'
    CONTAINER = 'container'
    OTHER = 'other'

    CHOICES = [
        (PHYSICAL, 'Physical Server'),
        (VIRTUAL, 'Virtual Machine'),
        (CLOUD, 'Cloud Instance'),
        (CONTAINER, 'Container'),
        (OTHER, 'Other'),
    ]

    DEFAULT = PHYSICAL


class PeripheralType(BaseChoices):
    """Types of peripheral devices."""
    PRINTER = 'printer'
    SCANNER = 'scanner'
    MULTIFUNCTION = 'multifunction'
    UPS = 'ups'
    NAS = 'nas'
    OTHER = 'other'

    CHOICES = [
        (PRINTER, 'Printer'),
        (SCANNER, 'Scanner'),
        (MULTIFUNCTION, 'Multifunction Printer'),
        (UPS, 'UPS'),
        (NAS, 'NAS'),
        (OTHER, 'Other'),
    ]

    DEFAULT = PRINTER


# =============================================================================
# Software Choices
# =============================================================================

class SoftwareType(BaseChoices):
    """Types of software."""
    MICROSOFT365 = 'microsoft365'
    ENDPOINT_PROTECTION = 'endpoint_protection'
    DESIGN = 'design'
    DEVELOPMENT = 'development'
    SUBSCRIPTION = 'subscription'
    OTHER = 'other'

    CHOICES = [
        (MICROSOFT365, 'Microsoft 365'),
        (ENDPOINT_PROTECTION, 'Endpoint Protection'),
        (DESIGN, 'Design/CAD'),
        (DEVELOPMENT, 'Development'),
        (SUBSCRIPTION, 'Subscription Service'),
        (OTHER, 'Other'),
    ]

    DEFAULT = OTHER


class LicenseType(BaseChoices):
    """Types of software/service licenses."""
    PERPETUAL = 'perpetual'
    SUBSCRIPTION = 'subscription'
    TRIAL = 'trial'
    FREE = 'free'
    OTHER = 'other'

    CHOICES = [
        (PERPETUAL, 'Perpetual'),
        (SUBSCRIPTION, 'Subscription'),
        (TRIAL, 'Trial'),
        (FREE, 'Free'),
        (OTHER, 'Other'),
    ]

    DEFAULT = PERPETUAL


# =============================================================================
# Backup Choices
# =============================================================================

class BackupType(BaseChoices):
    """Types of backup solutions."""
    SERVER = 'server'
    MICROSOFT365 = 'microsoft365'
    CLOUD = 'cloud'
    ENDPOINT = 'endpoint'
    DATABASE = 'database'
    NAS = 'nas'
    OTHER = 'other'

    CHOICES = [
        (SERVER, 'Server Backup'),
        (MICROSOFT365, 'Microsoft 365 Backup'),
        (CLOUD, 'Cloud Backup'),
        (ENDPOINT, 'Endpoint Backup'),
        (DATABASE, 'Database Backup'),
        (NAS, 'NAS Backup'),
        (OTHER, 'Other'),
    ]

    DEFAULT = OTHER


class BackupStatus(BaseChoices):
    """Status of backup jobs."""
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    FAILED = 'failed'
    WARNING = 'warning'

    CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
        (FAILED, 'Failed'),
        (WARNING, 'Warning'),
    ]

    DEFAULT = ACTIVE


# =============================================================================
# VoIP Choices
# =============================================================================

class VoIPType(BaseChoices):
    """Types of VoIP services."""
    TEAMS = 'teams'
    CX3 = '3cx'
    YEASTAR = 'yeastar'
    OTHER = 'other'

    CHOICES = [
        (TEAMS, 'Microsoft Teams'),
        (CX3, '3CX'),
        (YEASTAR, 'Yeastar'),
        (OTHER, 'Other'),
    ]

    DEFAULT = OTHER


# =============================================================================
# Registry of all choices for API exposure
# =============================================================================

CHOICES_REGISTRY = {
    'documentation_category': DocumentationCategory,
    'password_category': PasswordCategory,
    'configuration_type': ConfigurationType,
    'network_device_type': NetworkDeviceType,
    'endpoint_device_type': EndpointDeviceType,
    'server_type': ServerType,
    'peripheral_type': PeripheralType,
    'software_type': SoftwareType,
    'license_type': LicenseType,
    'backup_type': BackupType,
    'backup_status': BackupStatus,
    'voip_type': VoIPType,
}


def get_all_choices():
    """
    Get all choices as a dictionary for API response.

    Returns:
        dict: Dictionary with choice names as keys and list of {value, label} as values.

    Example response:
        {
            "documentation_category": [
                {"value": "procedure", "label": "Procedure"},
                {"value": "configuration", "label": "Configuration"},
                ...
            ],
            ...
        }
    """
    return {
        name: choice_class.to_dict_list()
        for name, choice_class in CHOICES_REGISTRY.items()
    }
