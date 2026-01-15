# Base models
from .base import SoftDeleteManager, BaseModel

# Organization models
from .organization import Organization, Location, Contact

# Membership models (for access control)
from .membership import OrganizationMember

# Unified version history (Single Source of Truth)
from .version import EntityVersion

# Documentation models
# Note: DocumentationVersion is deprecated, use EntityVersion instead
from .documentation import Documentation, DocumentationVersion

# Security models
# Note: PasswordEntryVersion is deprecated, use EntityVersion instead
from .security import PasswordEntry, PasswordEntryVersion

# Configuration models
# Note: ConfigurationVersion is deprecated, use EntityVersion instead
from .configuration import Configuration, ConfigurationVersion

# Network models
from .network import NetworkDevice, InternetConnection, ConnectionType

# Device models
from .devices import EndpointUser, Server, Peripheral

# Software models
from .software import Software, SoftwareAssignment

# Backup models
from .backup import Backup

# VoIP models
from .voip import VoIP, VoIPAssignment

__all__ = [
    # Base
    'SoftDeleteManager',
    'BaseModel',
    # Organization
    'Organization',
    'Location',
    'Contact',
    # Membership (access control)
    'OrganizationMember',
    # Unified Version History (new - Single Source of Truth)
    'EntityVersion',
    # Documentation
    'Documentation',
    'DocumentationVersion',  # Deprecated - kept for backward compatibility
    # Security
    'PasswordEntry',
    'PasswordEntryVersion',  # Deprecated - kept for backward compatibility
    # Configuration
    'Configuration',
    'ConfigurationVersion',  # Deprecated - kept for backward compatibility
    # Network
    'NetworkDevice',
    'InternetConnection',
    'ConnectionType',
    # Devices
    'EndpointUser',
    'Server',
    'Peripheral',
    # Software
    'Software',
    'SoftwareAssignment',
    # Backup
    'Backup',
    # VoIP
    'VoIP',
    'VoIPAssignment',
]
