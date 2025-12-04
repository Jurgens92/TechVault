"""
Export/Import service for complete organization data backup and restore.
"""
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid
from django.db import transaction
from django.contrib.auth import get_user_model
from core.models import (
    Organization, Location, Contact, NetworkDevice, Server,
    EndpointUser, Peripheral, Software, VoIP, Backup,
    Documentation, Configuration, PasswordEntry,
    SoftwareAssignment, VoIPAssignment
)

User = get_user_model()


class OrganizationExportImportService:
    """Service for exporting and importing complete organization data."""

    def __init__(self, user):
        """Initialize the service with the requesting user."""
        self.user = user

    def export_organizations(
        self,
        organization_ids: Optional[List[str]] = None,
        include_deleted: bool = False
    ) -> Dict[str, Any]:
        """
        Export complete organization data for backup purposes.

        Args:
            organization_ids: List of organization UUIDs to export (None = all)
            include_deleted: Whether to include soft-deleted records

        Returns:
            Dictionary containing complete organization data
        """
        # Get organizations to export
        if organization_ids:
            if include_deleted:
                organizations = Organization.all_objects.filter(id__in=organization_ids)
            else:
                organizations = Organization.objects.filter(id__in=organization_ids)
        else:
            if include_deleted:
                organizations = Organization.all_objects.all()
            else:
                organizations = Organization.objects.all()

        export_data = {
            'export_version': '1.0',
            'exported_at': datetime.now().isoformat(),
            'exported_by': self.user.email,
            'include_deleted': include_deleted,
            'organizations': []
        }

        for org in organizations:
            org_data = self._export_organization(org, include_deleted)
            export_data['organizations'].append(org_data)

        return export_data

    def _export_organization(self, org: Organization, include_deleted: bool) -> Dict[str, Any]:
        """Export a single organization with all related data."""
        # Get the appropriate manager based on include_deleted
        manager_suffix = '.all_objects' if include_deleted else '.objects'

        org_data = {
            'organization': {
                'id': str(org.id),
                'name': org.name,
                'description': org.description,
                'website': org.website,
                'phone': org.phone,
                'email': org.email,
                'address': org.address,
                'city': org.city,
                'state_province': org.state_province,
                'postal_code': org.postal_code,
                'country': org.country,
                'is_active': org.is_active,
                'created_at': org.created_at.isoformat(),
                'updated_at': org.updated_at.isoformat(),
                'deleted_at': org.deleted_at.isoformat() if org.deleted_at else None,
            },
            'locations': self._export_locations(org, include_deleted),
            'contacts': self._export_contacts(org, include_deleted),
            'documentations': self._export_documentations(org, include_deleted),
            'password_entries': self._export_password_entries(org, include_deleted),
            'configurations': self._export_configurations(org, include_deleted),
            'network_devices': self._export_network_devices(org, include_deleted),
            'endpoint_users': self._export_endpoint_users(org, include_deleted),
            'servers': self._export_servers(org, include_deleted),
            'peripherals': self._export_peripherals(org, include_deleted),
            'software': self._export_software(org, include_deleted),
            'voip': self._export_voip(org, include_deleted),
            'backups': self._export_backups(org, include_deleted),
        }

        return org_data

    def _get_manager(self, model, include_deleted: bool):
        """Get the appropriate manager based on include_deleted flag."""
        return model.all_objects if include_deleted else model.objects

    def _export_locations(self, org: Organization, include_deleted: bool) -> List[Dict]:
        """Export all locations for an organization."""
        manager = self._get_manager(Location, include_deleted)
        locations = manager.filter(organization=org)
        return [
            {
                'id': str(loc.id),
                'name': loc.name,
                'description': loc.description,
                'address': loc.address,
                'city': loc.city,
                'state_province': loc.state_province,
                'postal_code': loc.postal_code,
                'country': loc.country,
                'phone': loc.phone,
                'is_active': loc.is_active,
                'created_at': loc.created_at.isoformat(),
                'updated_at': loc.updated_at.isoformat(),
                'deleted_at': loc.deleted_at.isoformat() if loc.deleted_at else None,
            }
            for loc in locations
        ]

    def _export_contacts(self, org: Organization, include_deleted: bool) -> List[Dict]:
        """Export all contacts for an organization."""
        manager = self._get_manager(Contact, include_deleted)
        contacts = manager.filter(organization=org).select_related('location')
        return [
            {
                'id': str(contact.id),
                'location_id': str(contact.location.id) if contact.location else None,
                'first_name': contact.first_name,
                'last_name': contact.last_name,
                'title': contact.title,
                'email': contact.email,
                'phone': contact.phone,
                'mobile': contact.mobile,
                'notes': contact.notes,
                'is_active': contact.is_active,
                'created_at': contact.created_at.isoformat(),
                'updated_at': contact.updated_at.isoformat(),
                'deleted_at': contact.deleted_at.isoformat() if contact.deleted_at else None,
            }
            for contact in contacts
        ]

    def _export_documentations(self, org: Organization, include_deleted: bool) -> List[Dict]:
        """Export all documentation for an organization."""
        manager = self._get_manager(Documentation, include_deleted)
        docs = manager.filter(organization=org)
        return [
            {
                'id': str(doc.id),
                'title': doc.title,
                'content': doc.content,
                'category': doc.category,
                'tags': doc.tags,
                'is_published': doc.is_published,
                'version': doc.version,
                'created_at': doc.created_at.isoformat(),
                'updated_at': doc.updated_at.isoformat(),
                'deleted_at': doc.deleted_at.isoformat() if doc.deleted_at else None,
            }
            for doc in docs
        ]

    def _export_password_entries(self, org: Organization, include_deleted: bool) -> List[Dict]:
        """Export all password entries for an organization."""
        manager = self._get_manager(PasswordEntry, include_deleted)
        passwords = manager.filter(organization=org)
        return [
            {
                'id': str(pwd.id),
                'name': pwd.name,
                'username': pwd.username,
                'password': pwd.password,  # Exported as-is, encryption preserved
                'url': pwd.url,
                'notes': pwd.notes,
                'category': pwd.category,
                'is_encrypted': pwd.is_encrypted,
                'created_at': pwd.created_at.isoformat(),
                'updated_at': pwd.updated_at.isoformat(),
                'deleted_at': pwd.deleted_at.isoformat() if pwd.deleted_at else None,
            }
            for pwd in passwords
        ]

    def _export_configurations(self, org: Organization, include_deleted: bool) -> List[Dict]:
        """Export all configurations for an organization."""
        manager = self._get_manager(Configuration, include_deleted)
        configs = manager.filter(organization=org)
        return [
            {
                'id': str(config.id),
                'name': config.name,
                'config_type': config.config_type,
                'content': config.content,
                'description': config.description,
                'version': config.version,
                'is_active': config.is_active,
                'created_at': config.created_at.isoformat(),
                'updated_at': config.updated_at.isoformat(),
                'deleted_at': config.deleted_at.isoformat() if config.deleted_at else None,
            }
            for config in configs
        ]

    def _export_network_devices(self, org: Organization, include_deleted: bool) -> List[Dict]:
        """Export all network devices for an organization."""
        manager = self._get_manager(NetworkDevice, include_deleted)
        devices = manager.filter(organization=org).select_related('location')
        return [
            {
                'id': str(device.id),
                'location_id': str(device.location.id) if device.location else None,
                'name': device.name,
                'device_type': device.device_type,
                'internet_provider': device.internet_provider,
                'internet_speed': device.internet_speed,
                'manufacturer': device.manufacturer,
                'model': device.model,
                'ip_address': device.ip_address,
                'mac_address': device.mac_address,
                'serial_number': device.serial_number,
                'firmware_version': device.firmware_version,
                'notes': device.notes,
                'is_active': device.is_active,
                'created_at': device.created_at.isoformat(),
                'updated_at': device.updated_at.isoformat(),
                'deleted_at': device.deleted_at.isoformat() if device.deleted_at else None,
            }
            for device in devices
        ]

    def _export_endpoint_users(self, org: Organization, include_deleted: bool) -> List[Dict]:
        """Export all endpoint users for an organization."""
        manager = self._get_manager(EndpointUser, include_deleted)
        endpoints = manager.filter(organization=org).select_related('location', 'assigned_to')
        return [
            {
                'id': str(endpoint.id),
                'location_id': str(endpoint.location.id) if endpoint.location else None,
                'assigned_to_id': str(endpoint.assigned_to.id) if endpoint.assigned_to else None,
                'name': endpoint.name,
                'device_type': endpoint.device_type,
                'manufacturer': endpoint.manufacturer,
                'model': endpoint.model,
                'cpu': endpoint.cpu,
                'ram': endpoint.ram,
                'storage': endpoint.storage,
                'gpu': endpoint.gpu,
                'operating_system': endpoint.operating_system,
                'software_installed': endpoint.software_installed,
                'ip_address': endpoint.ip_address,
                'mac_address': endpoint.mac_address,
                'hostname': endpoint.hostname,
                'serial_number': endpoint.serial_number,
                'purchase_date': endpoint.purchase_date.isoformat() if endpoint.purchase_date else None,
                'warranty_expiry': endpoint.warranty_expiry.isoformat() if endpoint.warranty_expiry else None,
                'notes': endpoint.notes,
                'is_active': endpoint.is_active,
                'created_at': endpoint.created_at.isoformat(),
                'updated_at': endpoint.updated_at.isoformat(),
                'deleted_at': endpoint.deleted_at.isoformat() if endpoint.deleted_at else None,
            }
            for endpoint in endpoints
        ]

    def _export_servers(self, org: Organization, include_deleted: bool) -> List[Dict]:
        """Export all servers for an organization."""
        manager = self._get_manager(Server, include_deleted)
        servers = manager.filter(organization=org).select_related('location')
        return [
            {
                'id': str(server.id),
                'location_id': str(server.location.id) if server.location else None,
                'name': server.name,
                'server_type': server.server_type,
                'role': server.role,
                'manufacturer': server.manufacturer,
                'model': server.model,
                'cpu': server.cpu,
                'ram': server.ram,
                'storage': server.storage,
                'operating_system': server.operating_system,
                'software_installed': server.software_installed,
                'ip_address': server.ip_address,
                'mac_address': server.mac_address,
                'hostname': server.hostname,
                'serial_number': server.serial_number,
                'notes': server.notes,
                'is_active': server.is_active,
                'created_at': server.created_at.isoformat(),
                'updated_at': server.updated_at.isoformat(),
                'deleted_at': server.deleted_at.isoformat() if server.deleted_at else None,
            }
            for server in servers
        ]

    def _export_peripherals(self, org: Organization, include_deleted: bool) -> List[Dict]:
        """Export all peripherals for an organization."""
        manager = self._get_manager(Peripheral, include_deleted)
        peripherals = manager.filter(organization=org).select_related('location')
        return [
            {
                'id': str(peripheral.id),
                'location_id': str(peripheral.location.id) if peripheral.location else None,
                'name': peripheral.name,
                'device_type': peripheral.device_type,
                'manufacturer': peripheral.manufacturer,
                'model': peripheral.model,
                'ip_address': peripheral.ip_address,
                'mac_address': peripheral.mac_address,
                'serial_number': peripheral.serial_number,
                'notes': peripheral.notes,
                'is_active': peripheral.is_active,
                'created_at': peripheral.created_at.isoformat(),
                'updated_at': peripheral.updated_at.isoformat(),
                'deleted_at': peripheral.deleted_at.isoformat() if peripheral.deleted_at else None,
            }
            for peripheral in peripherals
        ]

    def _export_software(self, org: Organization, include_deleted: bool) -> List[Dict]:
        """Export all software licenses for an organization."""
        manager = self._get_manager(Software, include_deleted)
        software_list = manager.filter(organization=org).prefetch_related('software_assignments')

        result = []
        for software in software_list:
            assignment_manager = self._get_manager(SoftwareAssignment, include_deleted)
            assignments = assignment_manager.filter(software=software)

            result.append({
                'id': str(software.id),
                'name': software.name,
                'software_type': software.software_type,
                'license_key': software.license_key,
                'version': software.version,
                'license_type': software.license_type,
                'purchase_date': software.purchase_date.isoformat() if software.purchase_date else None,
                'expiry_date': software.expiry_date.isoformat() if software.expiry_date else None,
                'vendor': software.vendor,
                'quantity': software.quantity,
                'notes': software.notes,
                'is_active': software.is_active,
                'created_at': software.created_at.isoformat(),
                'updated_at': software.updated_at.isoformat(),
                'deleted_at': software.deleted_at.isoformat() if software.deleted_at else None,
                'assignments': [
                    {
                        'id': str(assignment.id),
                        'contact_id': str(assignment.contact.id),
                        'created_at': assignment.created_at.isoformat(),
                    }
                    for assignment in assignments
                ]
            })

        return result

    def _export_voip(self, org: Organization, include_deleted: bool) -> List[Dict]:
        """Export all VoIP services for an organization."""
        manager = self._get_manager(VoIP, include_deleted)
        voip_list = manager.filter(organization=org).prefetch_related('voip_assignments')

        result = []
        for voip in voip_list:
            assignment_manager = self._get_manager(VoIPAssignment, include_deleted)
            assignments = assignment_manager.filter(voip=voip)

            result.append({
                'id': str(voip.id),
                'name': voip.name,
                'voip_type': voip.voip_type,
                'license_key': voip.license_key,
                'version': voip.version,
                'license_type': voip.license_type,
                'purchase_date': voip.purchase_date.isoformat() if voip.purchase_date else None,
                'expiry_date': voip.expiry_date.isoformat() if voip.expiry_date else None,
                'vendor': voip.vendor,
                'quantity': voip.quantity,
                'phone_numbers': voip.phone_numbers,
                'extensions': voip.extensions,
                'notes': voip.notes,
                'is_active': voip.is_active,
                'created_at': voip.created_at.isoformat(),
                'updated_at': voip.updated_at.isoformat(),
                'deleted_at': voip.deleted_at.isoformat() if voip.deleted_at else None,
                'assignments': [
                    {
                        'id': str(assignment.id),
                        'contact_id': str(assignment.contact.id),
                        'extension': assignment.extension,
                        'phone_number': assignment.phone_number,
                        'created_at': assignment.created_at.isoformat(),
                    }
                    for assignment in assignments
                ]
            })

        return result

    def _export_backups(self, org: Organization, include_deleted: bool) -> List[Dict]:
        """Export all backup solutions for an organization."""
        manager = self._get_manager(Backup, include_deleted)
        backups = manager.filter(organization=org).select_related('location')
        return [
            {
                'id': str(backup.id),
                'location_id': str(backup.location.id) if backup.location else None,
                'name': backup.name,
                'backup_type': backup.backup_type,
                'vendor': backup.vendor,
                'frequency': backup.frequency,
                'retention_period': backup.retention_period,
                'storage_location': backup.storage_location,
                'storage_capacity': backup.storage_capacity,
                'target_systems': backup.target_systems,
                'last_backup_date': backup.last_backup_date.isoformat() if backup.last_backup_date else None,
                'next_backup_date': backup.next_backup_date.isoformat() if backup.next_backup_date else None,
                'backup_status': backup.backup_status,
                'notes': backup.notes,
                'is_active': backup.is_active,
                'created_at': backup.created_at.isoformat(),
                'updated_at': backup.updated_at.isoformat(),
                'deleted_at': backup.deleted_at.isoformat() if backup.deleted_at else None,
            }
            for backup in backups
        ]

    def import_organizations(
        self,
        import_data: Dict[str, Any],
        overwrite_existing: bool = False,
        preserve_ids: bool = False
    ) -> Dict[str, Any]:
        """
        Import organization data from an export file.

        Args:
            import_data: Dictionary containing exported organization data
            overwrite_existing: If True, update existing organizations with same name
            preserve_ids: If True, preserve original UUIDs (may cause conflicts)

        Returns:
            Dictionary with import results (success count, errors, etc.)
        """
        results = {
            'success': True,
            'imported_organizations': [],
            'skipped_organizations': [],
            'errors': []
        }

        if not import_data.get('organizations'):
            results['success'] = False
            results['errors'].append('No organizations found in import data')
            return results

        for org_data in import_data['organizations']:
            try:
                org_result = self._import_organization(
                    org_data,
                    overwrite_existing=overwrite_existing,
                    preserve_ids=preserve_ids
                )

                if org_result['success']:
                    results['imported_organizations'].append(org_result['organization_name'])
                else:
                    results['skipped_organizations'].append({
                        'name': org_result['organization_name'],
                        'reason': org_result.get('reason', 'Unknown error')
                    })
            except Exception as e:
                results['errors'].append({
                    'organization': org_data.get('organization', {}).get('name', 'Unknown'),
                    'error': str(e)
                })

        return results

    @transaction.atomic
    def _import_organization(
        self,
        org_data: Dict[str, Any],
        overwrite_existing: bool,
        preserve_ids: bool
    ) -> Dict[str, Any]:
        """Import a single organization with all related data."""
        org_info = org_data['organization']
        org_name = org_info['name']

        # Check if organization already exists (check ALL records, including soft-deleted)
        # Use all_objects to bypass the soft delete filter
        existing_org = Organization.all_objects.filter(name=org_name).first()

        if existing_org and not overwrite_existing:
            return {
                'success': False,
                'organization_name': org_name,
                'reason': 'Organization already exists and overwrite_existing is False'
            }

        # Create or update organization
        if existing_org and overwrite_existing:
            org = existing_org
            # Update organization fields
            org.description = org_info.get('description', '')
            org.website = org_info.get('website', '')
            org.phone = org_info.get('phone', '')
            org.email = org_info.get('email', '')
            org.address = org_info.get('address', '')
            org.city = org_info.get('city', '')
            org.state_province = org_info.get('state_province', '')
            org.postal_code = org_info.get('postal_code', '')
            org.country = org_info.get('country', '')
            org.is_active = org_info.get('is_active', True)
            org.created_by = self.user
            org.save()

            # Delete all existing related data to avoid conflicts
            # Use hard_delete to permanently remove them
            org.locations.all().hard_delete()
            org.contacts.all().hard_delete()
            org.documentations.all().hard_delete()
            org.password_entries.all().hard_delete()
            org.configurations.all().hard_delete()
            org.network_devices.all().hard_delete()
            org.endpoint_users.all().hard_delete()
            org.servers.all().hard_delete()
            org.peripherals.all().hard_delete()
            org.software.all().hard_delete()
            org.voip.all().hard_delete()
            org.backups.all().hard_delete()
        else:
            # Create new organization
            org_id = uuid.UUID(org_info['id']) if preserve_ids else uuid.uuid4()
            org = Organization(
                id=org_id,
                name=org_name,
                description=org_info.get('description', ''),
                website=org_info.get('website', ''),
                phone=org_info.get('phone', ''),
                email=org_info.get('email', ''),
                address=org_info.get('address', ''),
                city=org_info.get('city', ''),
                state_province=org_info.get('state_province', ''),
                postal_code=org_info.get('postal_code', ''),
                country=org_info.get('country', ''),
                is_active=org_info.get('is_active', True),
                created_by=self.user
            )
            org.save()

        # Track ID mappings for references
        location_id_map = {}
        contact_id_map = {}

        # Import locations first (needed for other entities)
        for loc_data in org_data.get('locations', []):
            old_id = loc_data['id']
            new_id = uuid.UUID(old_id) if preserve_ids else uuid.uuid4()

            location = Location(
                id=new_id,
                organization=org,
                name=loc_data['name'],
                description=loc_data.get('description', ''),
                address=loc_data['address'],
                city=loc_data['city'],
                state_province=loc_data.get('state_province', ''),
                postal_code=loc_data['postal_code'],
                country=loc_data['country'],
                phone=loc_data.get('phone', ''),
                is_active=loc_data.get('is_active', True),
                created_by=self.user
            )
            location.save()
            location_id_map[old_id] = new_id

        # Import contacts (needed for assignments)
        for contact_data in org_data.get('contacts', []):
            old_id = contact_data['id']
            new_id = uuid.UUID(old_id) if preserve_ids else uuid.uuid4()

            location_id = contact_data.get('location_id')
            location = None
            if location_id and location_id in location_id_map:
                location = Location.objects.get(id=location_id_map[location_id])

            contact = Contact(
                id=new_id,
                organization=org,
                location=location,
                first_name=contact_data['first_name'],
                last_name=contact_data['last_name'],
                title=contact_data.get('title', ''),
                email=contact_data['email'],
                phone=contact_data.get('phone', ''),
                mobile=contact_data.get('mobile', ''),
                notes=contact_data.get('notes', ''),
                is_active=contact_data.get('is_active', True),
                created_by=self.user
            )
            contact.save()
            contact_id_map[old_id] = new_id

        # Import documentation
        for doc_data in org_data.get('documentations', []):
            new_id = uuid.UUID(doc_data['id']) if preserve_ids else uuid.uuid4()

            doc = Documentation(
                id=new_id,
                organization=org,
                title=doc_data['title'],
                content=doc_data['content'],
                category=doc_data.get('category', 'other'),
                tags=doc_data.get('tags', ''),
                is_published=doc_data.get('is_published', False),
                version=doc_data.get('version', 1),
                created_by=self.user
            )
            doc.save()

        # Import password entries
        for pwd_data in org_data.get('password_entries', []):
            new_id = uuid.UUID(pwd_data['id']) if preserve_ids else uuid.uuid4()

            pwd = PasswordEntry(
                id=new_id,
                organization=org,
                name=pwd_data['name'],
                username=pwd_data.get('username', ''),
                password=pwd_data['password'],
                url=pwd_data.get('url', ''),
                notes=pwd_data.get('notes', ''),
                category=pwd_data.get('category', 'other'),
                is_encrypted=pwd_data.get('is_encrypted', False),
                created_by=self.user
            )
            pwd.save()

        # Import configurations
        for config_data in org_data.get('configurations', []):
            new_id = uuid.UUID(config_data['id']) if preserve_ids else uuid.uuid4()

            config = Configuration(
                id=new_id,
                organization=org,
                name=config_data['name'],
                config_type=config_data.get('config_type', 'other'),
                content=config_data['content'],
                description=config_data.get('description', ''),
                version=config_data.get('version', ''),
                is_active=config_data.get('is_active', True),
                created_by=self.user
            )
            config.save()

        # Import network devices
        for device_data in org_data.get('network_devices', []):
            new_id = uuid.UUID(device_data['id']) if preserve_ids else uuid.uuid4()

            location_id = device_data.get('location_id')
            location = None
            if location_id and location_id in location_id_map:
                location = Location.objects.get(id=location_id_map[location_id])

            device = NetworkDevice(
                id=new_id,
                organization=org,
                location=location,
                name=device_data['name'],
                device_type=device_data.get('device_type', 'other'),
                internet_provider=device_data.get('internet_provider', ''),
                internet_speed=device_data.get('internet_speed', ''),
                manufacturer=device_data.get('manufacturer', ''),
                model=device_data.get('model', ''),
                ip_address=device_data.get('ip_address', ''),
                mac_address=device_data.get('mac_address', ''),
                serial_number=device_data.get('serial_number', ''),
                firmware_version=device_data.get('firmware_version', ''),
                notes=device_data.get('notes', ''),
                is_active=device_data.get('is_active', True),
                created_by=self.user
            )
            device.save()

        # Import endpoint users
        for endpoint_data in org_data.get('endpoint_users', []):
            new_id = uuid.UUID(endpoint_data['id']) if preserve_ids else uuid.uuid4()

            location_id = endpoint_data.get('location_id')
            location = None
            if location_id and location_id in location_id_map:
                location = Location.objects.get(id=location_id_map[location_id])

            assigned_to_id = endpoint_data.get('assigned_to_id')
            assigned_to = None
            if assigned_to_id and assigned_to_id in contact_id_map:
                assigned_to = Contact.objects.get(id=contact_id_map[assigned_to_id])

            endpoint = EndpointUser(
                id=new_id,
                organization=org,
                location=location,
                assigned_to=assigned_to,
                name=endpoint_data['name'],
                device_type=endpoint_data.get('device_type', 'desktop'),
                manufacturer=endpoint_data.get('manufacturer', ''),
                model=endpoint_data.get('model', ''),
                cpu=endpoint_data.get('cpu', ''),
                ram=endpoint_data.get('ram', ''),
                storage=endpoint_data.get('storage', ''),
                gpu=endpoint_data.get('gpu', ''),
                operating_system=endpoint_data.get('operating_system', ''),
                software_installed=endpoint_data.get('software_installed', ''),
                ip_address=endpoint_data.get('ip_address', ''),
                mac_address=endpoint_data.get('mac_address', ''),
                hostname=endpoint_data.get('hostname', ''),
                serial_number=endpoint_data.get('serial_number', ''),
                purchase_date=endpoint_data.get('purchase_date'),
                warranty_expiry=endpoint_data.get('warranty_expiry'),
                notes=endpoint_data.get('notes', ''),
                is_active=endpoint_data.get('is_active', True),
                created_by=self.user
            )
            endpoint.save()

        # Import servers
        for server_data in org_data.get('servers', []):
            new_id = uuid.UUID(server_data['id']) if preserve_ids else uuid.uuid4()

            location_id = server_data.get('location_id')
            location = None
            if location_id and location_id in location_id_map:
                location = Location.objects.get(id=location_id_map[location_id])

            server = Server(
                id=new_id,
                organization=org,
                location=location,
                name=server_data['name'],
                server_type=server_data.get('server_type', 'physical'),
                role=server_data.get('role', ''),
                manufacturer=server_data.get('manufacturer', ''),
                model=server_data.get('model', ''),
                cpu=server_data.get('cpu', ''),
                ram=server_data.get('ram', ''),
                storage=server_data.get('storage', ''),
                operating_system=server_data.get('operating_system', ''),
                software_installed=server_data.get('software_installed', ''),
                ip_address=server_data.get('ip_address', ''),
                mac_address=server_data.get('mac_address', ''),
                hostname=server_data.get('hostname', ''),
                serial_number=server_data.get('serial_number', ''),
                notes=server_data.get('notes', ''),
                is_active=server_data.get('is_active', True),
                created_by=self.user
            )
            server.save()

        # Import peripherals
        for peripheral_data in org_data.get('peripherals', []):
            new_id = uuid.UUID(peripheral_data['id']) if preserve_ids else uuid.uuid4()

            location_id = peripheral_data.get('location_id')
            location = None
            if location_id and location_id in location_id_map:
                location = Location.objects.get(id=location_id_map[location_id])

            peripheral = Peripheral(
                id=new_id,
                organization=org,
                location=location,
                name=peripheral_data['name'],
                device_type=peripheral_data.get('device_type', 'printer'),
                manufacturer=peripheral_data.get('manufacturer', ''),
                model=peripheral_data.get('model', ''),
                ip_address=peripheral_data.get('ip_address', ''),
                mac_address=peripheral_data.get('mac_address', ''),
                serial_number=peripheral_data.get('serial_number', ''),
                notes=peripheral_data.get('notes', ''),
                is_active=peripheral_data.get('is_active', True),
                created_by=self.user
            )
            peripheral.save()

        # Import software licenses and assignments
        for software_data in org_data.get('software', []):
            new_id = uuid.UUID(software_data['id']) if preserve_ids else uuid.uuid4()

            software = Software(
                id=new_id,
                organization=org,
                name=software_data['name'],
                software_type=software_data.get('software_type', 'other'),
                license_key=software_data.get('license_key', ''),
                version=software_data.get('version', ''),
                license_type=software_data.get('license_type', 'perpetual'),
                purchase_date=software_data.get('purchase_date'),
                expiry_date=software_data.get('expiry_date'),
                vendor=software_data.get('vendor', ''),
                quantity=software_data.get('quantity', 1),
                notes=software_data.get('notes', ''),
                is_active=software_data.get('is_active', True),
                created_by=self.user
            )
            software.save()

            # Import software assignments
            for assignment_data in software_data.get('assignments', []):
                contact_id = assignment_data['contact_id']
                if contact_id in contact_id_map:
                    contact = Contact.objects.get(id=contact_id_map[contact_id])
                    assignment_id = uuid.UUID(assignment_data['id']) if preserve_ids else uuid.uuid4()

                    assignment = SoftwareAssignment(
                        id=assignment_id,
                        software=software,
                        contact=contact,
                        created_by=self.user
                    )
                    assignment.save()

        # Import VoIP services and assignments
        for voip_data in org_data.get('voip', []):
            new_id = uuid.UUID(voip_data['id']) if preserve_ids else uuid.uuid4()

            voip = VoIP(
                id=new_id,
                organization=org,
                name=voip_data['name'],
                voip_type=voip_data.get('voip_type', 'other'),
                license_key=voip_data.get('license_key', ''),
                version=voip_data.get('version', ''),
                license_type=voip_data.get('license_type', 'subscription'),
                purchase_date=voip_data.get('purchase_date'),
                expiry_date=voip_data.get('expiry_date'),
                vendor=voip_data.get('vendor', ''),
                quantity=voip_data.get('quantity', 1),
                phone_numbers=voip_data.get('phone_numbers', ''),
                extensions=voip_data.get('extensions', ''),
                notes=voip_data.get('notes', ''),
                is_active=voip_data.get('is_active', True),
                created_by=self.user
            )
            voip.save()

            # Import VoIP assignments
            for assignment_data in voip_data.get('assignments', []):
                contact_id = assignment_data['contact_id']
                if contact_id in contact_id_map:
                    contact = Contact.objects.get(id=contact_id_map[contact_id])
                    assignment_id = uuid.UUID(assignment_data['id']) if preserve_ids else uuid.uuid4()

                    assignment = VoIPAssignment(
                        id=assignment_id,
                        voip=voip,
                        contact=contact,
                        extension=assignment_data.get('extension', ''),
                        phone_number=assignment_data.get('phone_number', ''),
                        created_by=self.user
                    )
                    assignment.save()

        # Import backups
        for backup_data in org_data.get('backups', []):
            new_id = uuid.UUID(backup_data['id']) if preserve_ids else uuid.uuid4()

            location_id = backup_data.get('location_id')
            location = None
            if location_id and location_id in location_id_map:
                location = Location.objects.get(id=location_id_map[location_id])

            backup = Backup(
                id=new_id,
                organization=org,
                location=location,
                name=backup_data['name'],
                backup_type=backup_data.get('backup_type', 'other'),
                vendor=backup_data.get('vendor', ''),
                frequency=backup_data.get('frequency', ''),
                retention_period=backup_data.get('retention_period', ''),
                storage_location=backup_data.get('storage_location', ''),
                storage_capacity=backup_data.get('storage_capacity', ''),
                target_systems=backup_data.get('target_systems', ''),
                last_backup_date=backup_data.get('last_backup_date'),
                next_backup_date=backup_data.get('next_backup_date'),
                backup_status=backup_data.get('backup_status', 'active'),
                notes=backup_data.get('notes', ''),
                is_active=backup_data.get('is_active', True),
                created_by=self.user
            )
            backup.save()

        return {
            'success': True,
            'organization_name': org_name
        }
