"""
Report generation services for TechVault.
"""
from datetime import datetime
from typing import Dict, List, Any, Optional
from django.db.models import Count, Q
from core.models import (
    Organization, Location, Contact, NetworkDevice, Server,
    EndpointUser, Peripheral, Software, VoIP, Backup,
    Documentation, Configuration, PasswordEntry
)


class ReportService:
    """Service for generating various types of reports."""

    def __init__(self, user):
        """Initialize the report service with the requesting user."""
        self.user = user

    def generate_organization_report(
        self,
        organization_id: str,
        include_sections: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive report for an organization.

        Args:
            organization_id: UUID of the organization
            include_sections: List of sections to include (default: all)
                Options: 'locations', 'contacts', 'network_devices', 'servers',
                        'endpoints', 'peripherals', 'software', 'voip', 'backups',
                        'documentation', 'configurations', 'passwords'

        Returns:
            Dictionary containing the report data
        """
        try:
            org = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise ValueError(f"Organization with ID {organization_id} not found")

        # Default to all sections if none specified
        if include_sections is None:
            include_sections = [
                'locations', 'contacts', 'network_devices', 'servers',
                'endpoints', 'peripherals', 'software', 'voip', 'backups',
                'documentation', 'configurations', 'passwords'
            ]

        report = {
            'report_type': 'organization',
            'generated_at': datetime.now().isoformat(),
            'generated_by': self.user.email,
            'organization': {
                'id': str(org.id),
                'name': org.name,
                'address': org.address,
                'city': org.city,
                'state': org.state_province,
                'postal_code': org.postal_code,
                'country': org.country,
                'phone': org.phone,
                'email': org.email,
                'website': org.website,
            },
            'sections': {}
        }

        # Generate each section based on what's requested
        if 'locations' in include_sections:
            report['sections']['locations'] = self._get_locations(org)

        if 'contacts' in include_sections:
            report['sections']['contacts'] = self._get_contacts(org)

        if 'network_devices' in include_sections:
            report['sections']['network_devices'] = self._get_network_devices(org)

        if 'servers' in include_sections:
            report['sections']['servers'] = self._get_servers(org)

        if 'endpoints' in include_sections:
            report['sections']['endpoints'] = self._get_endpoints(org)

        if 'peripherals' in include_sections:
            report['sections']['peripherals'] = self._get_peripherals(org)

        if 'software' in include_sections:
            report['sections']['software'] = self._get_software(org)

        if 'voip' in include_sections:
            report['sections']['voip'] = self._get_voip(org)

        if 'backups' in include_sections:
            report['sections']['backups'] = self._get_backups(org)

        if 'documentation' in include_sections:
            report['sections']['documentation'] = self._get_documentation(org)

        if 'configurations' in include_sections:
            report['sections']['configurations'] = self._get_configurations(org)

        if 'passwords' in include_sections:
            # Only include password metadata, not actual passwords
            report['sections']['passwords'] = self._get_password_metadata(org)

        # Add summary statistics
        report['summary'] = self._generate_summary(report['sections'])

        return report

    def generate_location_report(
        self,
        location_id: str,
        include_sections: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate a comprehensive report for a specific location."""
        try:
            location = Location.objects.select_related('organization').get(id=location_id)
        except Location.DoesNotExist:
            raise ValueError(f"Location with ID {location_id} not found")

        # Default to all sections if none specified
        if include_sections is None:
            include_sections = [
                'contacts', 'network_devices', 'servers',
                'endpoints', 'peripherals', 'backups', 'documentation'
            ]

        report = {
            'report_type': 'location',
            'generated_at': datetime.now().isoformat(),
            'generated_by': self.user.email,
            'organization': {
                'id': str(location.organization.id),
                'name': location.organization.name,
            },
            'location': {
                'id': str(location.id),
                'name': location.name,
                'address': location.address,
                'city': location.city,
                'state': location.state_province,
                'postal_code': location.postal_code,
                'country': location.country,
            },
            'sections': {}
        }

        # Generate each section for the specific location
        if 'contacts' in include_sections:
            contacts = Contact.objects.filter(location=location)
            report['sections']['contacts'] = [self._format_contact(c) for c in contacts]

        if 'network_devices' in include_sections:
            devices = NetworkDevice.objects.filter(location=location)
            report['sections']['network_devices'] = [self._format_network_device(d) for d in devices]

        if 'servers' in include_sections:
            servers = Server.objects.filter(location=location)
            report['sections']['servers'] = [self._format_server(s) for s in servers]

        if 'endpoints' in include_sections:
            endpoints = EndpointUser.objects.filter(location=location)
            report['sections']['endpoints'] = [self._format_endpoint(e) for e in endpoints]

        if 'peripherals' in include_sections:
            peripherals = Peripheral.objects.filter(location=location)
            report['sections']['peripherals'] = [self._format_peripheral(p) for p in peripherals]

        if 'backups' in include_sections:
            backups = Backup.objects.filter(location=location)
            report['sections']['backups'] = [self._format_backup(b) for b in backups]

        if 'documentation' in include_sections:
            docs = Documentation.objects.filter(location=location)
            report['sections']['documentation'] = [self._format_documentation(d) for d in docs]

        # Add summary statistics
        report['summary'] = self._generate_summary(report['sections'])

        return report

    def generate_asset_inventory_report(
        self,
        organization_id: Optional[str] = None,
        location_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate an asset inventory report."""
        report = {
            'report_type': 'asset_inventory',
            'generated_at': datetime.now().isoformat(),
            'generated_by': self.user.email,
            'assets': {
                'network_devices': [],
                'servers': [],
                'endpoints': [],
                'peripherals': [],
            }
        }

        filters = {}
        if organization_id:
            filters['organization_id'] = organization_id
            org = Organization.objects.get(id=organization_id)
            report['organization'] = {'id': str(org.id), 'name': org.name}
        if location_id:
            filters['location_id'] = location_id
            location = Location.objects.get(id=location_id)
            report['location'] = {'id': str(location.id), 'name': location.name}

        # Get all assets with the filters
        report['assets']['network_devices'] = [
            self._format_network_device(d)
            for d in NetworkDevice.objects.filter(**filters)
        ]
        report['assets']['servers'] = [
            self._format_server(s)
            for s in Server.objects.filter(**filters)
        ]
        report['assets']['endpoints'] = [
            self._format_endpoint(e)
            for e in EndpointUser.objects.filter(**filters)
        ]
        report['assets']['peripherals'] = [
            self._format_peripheral(p)
            for p in Peripheral.objects.filter(**filters)
        ]

        # Calculate totals
        report['totals'] = {
            'network_devices': len(report['assets']['network_devices']),
            'servers': len(report['assets']['servers']),
            'endpoints': len(report['assets']['endpoints']),
            'peripherals': len(report['assets']['peripherals']),
            'total_assets': sum([
                len(report['assets']['network_devices']),
                len(report['assets']['servers']),
                len(report['assets']['endpoints']),
                len(report['assets']['peripherals']),
            ])
        }

        return report

    def generate_software_license_report(
        self,
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a software license report showing all licenses and their status."""
        report = {
            'report_type': 'software_license',
            'generated_at': datetime.now().isoformat(),
            'generated_by': self.user.email,
            'licenses': []
        }

        filters = {}
        if organization_id:
            filters['organization_id'] = organization_id
            org = Organization.objects.get(id=organization_id)
            report['organization'] = {'id': str(org.id), 'name': org.name}

        software_list = Software.objects.filter(**filters).prefetch_related('software_assignments', 'software_assignments__contact')

        for software in software_list:
            license_data = {
                'id': str(software.id),
                'name': software.name,
                'vendor': software.vendor,
                'version': software.version,
                'license_type': software.license_type,
                'license_key': software.license_key,
                'purchase_date': software.purchase_date.isoformat() if software.purchase_date else None,
                'expiry_date': software.expiry_date.isoformat() if software.expiry_date else None,
                'seats_total': software.quantity,
                'seats_used': software.software_assignments.count(),
                'seats_available': software.quantity - software.software_assignments.count() if software.quantity else None,
                'status': self._get_license_status(software),
                'assignments': [
                    {
                        'contact_id': str(assignment.contact.id),
                        'contact_name': assignment.contact.full_name,
                        'contact_email': assignment.contact.email,
                        'assigned_at': assignment.created_at.isoformat()
                    }
                    for assignment in software.software_assignments.all()
                ]
            }
            report['licenses'].append(license_data)

        # Add summary statistics
        report['summary'] = {
            'total_licenses': len(report['licenses']),
            'expiring_soon': len([l for l in report['licenses'] if l['status'] == 'expiring_soon']),
            'expired': len([l for l in report['licenses'] if l['status'] == 'expired']),
            'active': len([l for l in report['licenses'] if l['status'] == 'active']),
            'over_capacity': len([l for l in report['licenses'] if l.get('seats_available', 0) < 0]),
        }

        return report

    # Helper methods for formatting data

    def _get_locations(self, org):
        """Get all locations for an organization."""
        locations = Location.objects.filter(organization=org)
        return [
            {
                'id': str(loc.id),
                'name': loc.name,
                'address': loc.address,
                'city': loc.city,
                'state': loc.state_province,
                'postal_code': loc.postal_code,
                'country': loc.country,
            }
            for loc in locations
        ]

    def _get_contacts(self, org):
        """Get all contacts for an organization."""
        contacts = Contact.objects.filter(organization=org).select_related('location')
        return [self._format_contact(c) for c in contacts]

    def _format_contact(self, contact):
        """Format contact data."""
        return {
            'id': str(contact.id),
            'name': contact.full_name,
            'title': contact.title,
            'email': contact.email,
            'phone': contact.phone,
            'mobile': contact.mobile,
            'location': contact.location.name if contact.location else None,
            'notes': contact.notes,
        }

    def _get_network_devices(self, org):
        """Get all network devices for an organization."""
        devices = NetworkDevice.objects.filter(organization=org).select_related('location')
        return [self._format_network_device(d) for d in devices]

    def _format_network_device(self, device):
        """Format network device data."""
        return {
            'id': str(device.id),
            'name': device.name,
            'device_type': device.device_type,
            'manufacturer': device.manufacturer,
            'model': device.model,
            'ip_address': device.ip_address,
            'mac_address': device.mac_address,
            'location': device.location.name if device.location else None,
            'status': device.status,
            'internet_speed_down': device.internet_speed_down,
            'internet_speed_up': device.internet_speed_up,
        }

    def _get_servers(self, org):
        """Get all servers for an organization."""
        servers = Server.objects.filter(organization=org).select_related('location')
        return [self._format_server(s) for s in servers]

    def _format_server(self, server):
        """Format server data."""
        return {
            'id': str(server.id),
            'name': server.name,
            'server_type': server.server_type,
            'operating_system': server.operating_system,
            'os_version': server.os_version,
            'cpu_model': server.cpu_model,
            'cpu_cores': server.cpu_cores,
            'ram_gb': server.ram_gb,
            'storage_gb': server.storage_gb,
            'ip_address': server.ip_address,
            'location': server.location.name if server.location else None,
            'status': server.status,
            'virtualization_platform': server.virtualization_platform,
        }

    def _get_endpoints(self, org):
        """Get all endpoints for an organization."""
        endpoints = EndpointUser.objects.filter(organization=org).select_related('location', 'contact')
        return [self._format_endpoint(e) for e in endpoints]

    def _format_endpoint(self, endpoint):
        """Format endpoint data."""
        return {
            'id': str(endpoint.id),
            'name': endpoint.name,
            'device_type': endpoint.device_type,
            'manufacturer': endpoint.manufacturer,
            'model': endpoint.model,
            'operating_system': endpoint.operating_system,
            'os_version': endpoint.os_version,
            'cpu_model': endpoint.cpu_model,
            'ram_gb': endpoint.ram_gb,
            'storage_gb': endpoint.storage_gb,
            'serial_number': endpoint.serial_number,
            'location': endpoint.location.name if endpoint.location else None,
            'assigned_to': endpoint.contact.full_name if endpoint.contact else None,
            'status': endpoint.status,
        }

    def _get_peripherals(self, org):
        """Get all peripherals for an organization."""
        peripherals = Peripheral.objects.filter(organization=org).select_related('location', 'contact')
        return [self._format_peripheral(p) for p in peripherals]

    def _format_peripheral(self, peripheral):
        """Format peripheral data."""
        return {
            'id': str(peripheral.id),
            'name': peripheral.name,
            'device_type': peripheral.device_type,
            'manufacturer': peripheral.manufacturer,
            'model': peripheral.model,
            'serial_number': peripheral.serial_number,
            'ip_address': peripheral.ip_address,
            'location': peripheral.location.name if peripheral.location else None,
            'assigned_to': peripheral.contact.full_name if peripheral.contact else None,
            'status': peripheral.status,
        }

    def _get_software(self, org):
        """Get all software for an organization."""
        software_list = Software.objects.filter(organization=org).prefetch_related('software_assignments')
        return [
            {
                'id': str(software.id),
                'name': software.name,
                'vendor': software.vendor,
                'version': software.version,
                'license_type': software.license_type,
                'expiry_date': software.expiry_date.isoformat() if software.expiry_date else None,
                'seats_total': software.quantity,
                'seats_used': software.software_assignments.count(),
                'status': self._get_license_status(software),
            }
            for software in software_list
        ]

    def _get_voip(self, org):
        """Get all VoIP services for an organization."""
        voip_services = VoIP.objects.filter(organization=org).prefetch_related('voip_assignments')
        return [
            {
                'id': str(voip.id),
                'name': voip.name,
                'vendor': voip.vendor,
                'voip_type': voip.voip_type,
                'license_key': voip.license_key,
                'extensions_total': voip.quantity,
                'extensions_used': voip.voip_assignments.count(),
            }
            for voip in voip_services
        ]

    def _get_backups(self, org):
        """Get all backups for an organization."""
        backups = Backup.objects.filter(organization=org).select_related('location')
        return [self._format_backup(b) for b in backups]

    def _format_backup(self, backup):
        """Format backup data."""
        return {
            'id': str(backup.id),
            'name': backup.name,
            'backup_type': backup.backup_type,
            'vendor': backup.vendor,
            'target_systems': backup.target_systems,
            'storage_location': backup.storage_location,
            'frequency': backup.frequency,
            'retention_period': backup.retention_period,
            'last_backup': backup.last_backup_date.isoformat() if backup.last_backup_date else None,
            'status': backup.backup_status,
            'location': backup.location.name if backup.location else None,
        }

    def _get_documentation(self, org):
        """Get all documentation for an organization."""
        docs = Documentation.objects.filter(organization=org).select_related('location')
        return [self._format_documentation(d) for d in docs]

    def _format_documentation(self, doc):
        """Format documentation data."""
        return {
            'id': str(doc.id),
            'title': doc.title,
            'category': doc.category,
            'location': doc.location.name if doc.location else None,
            'is_published': doc.is_published,
            'created_at': doc.created_at.isoformat(),
            'updated_at': doc.updated_at.isoformat(),
        }

    def _get_configurations(self, org):
        """Get all configurations for an organization."""
        configs = Configuration.objects.filter(organization=org).select_related('location')
        return [
            {
                'id': str(config.id),
                'name': config.name,
                'config_type': config.config_type,
                'location': config.location.name if config.location else None,
                'created_at': config.created_at.isoformat(),
                'updated_at': config.updated_at.isoformat(),
            }
            for config in configs
        ]

    def _get_password_metadata(self, org):
        """Get password metadata (not actual passwords) for an organization."""
        passwords = PasswordEntry.objects.filter(organization=org).select_related('location')
        return [
            {
                'id': str(pwd.id),
                'title': pwd.title,
                'category': pwd.category,
                'username': pwd.username,
                'url': pwd.url,
                'location': pwd.location.name if pwd.location else None,
                'created_at': pwd.created_at.isoformat(),
                'updated_at': pwd.updated_at.isoformat(),
            }
            for pwd in passwords
        ]

    def _get_license_status(self, software):
        """Determine the status of a software license."""
        from datetime import datetime, timedelta

        if software.expiry_date:
            today = datetime.now().date()
            days_until_expiry = (software.expiry_date - today).days

            if days_until_expiry < 0:
                return 'expired'
            elif days_until_expiry <= 30:
                return 'expiring_soon'

        if software.quantity and software.software_assignments.count() > software.quantity:
            return 'over_capacity'

        return 'active'

    def _generate_summary(self, sections):
        """Generate summary statistics for the report."""
        summary = {}

        for section_name, section_data in sections.items():
            if isinstance(section_data, list):
                summary[f'{section_name}_count'] = len(section_data)

        return summary
