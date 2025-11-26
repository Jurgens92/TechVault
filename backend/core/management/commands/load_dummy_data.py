"""
Django management command to load dummy data for TechVault application.

Usage:
    python manage.py load_dummy_data
    python manage.py load_dummy_data --clear  # Clear existing data first
"""

import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from core.models import (
    Organization, Location, Contact, Documentation, PasswordEntry,
    Configuration, NetworkDevice, EndpointUser, Server, Peripheral
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Load dummy data into the database for testing and development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing data before loading dummy data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_data()
            self.stdout.write(self.style.SUCCESS('Data cleared successfully'))

        self.stdout.write(self.style.SUCCESS('Loading dummy data...'))

        with transaction.atomic():
            # Create users
            users = self.create_users()
            self.stdout.write(self.style.SUCCESS(f'Created {len(users)} users'))

            # Create organizations
            organizations = self.create_organizations(users)
            self.stdout.write(self.style.SUCCESS(f'Created {len(organizations)} organizations'))

            # Create locations
            locations = self.create_locations(organizations, users)
            self.stdout.write(self.style.SUCCESS(f'Created {len(locations)} locations'))

            # Create contacts
            contacts = self.create_contacts(organizations, locations, users)
            self.stdout.write(self.style.SUCCESS(f'Created {len(contacts)} contacts'))

            # Create documentation
            documentations = self.create_documentations(organizations, users)
            self.stdout.write(self.style.SUCCESS(f'Created {len(documentations)} documentation entries'))

            # Create password entries
            password_entries = self.create_password_entries(organizations, users)
            self.stdout.write(self.style.SUCCESS(f'Created {len(password_entries)} password entries'))

            # Create configurations
            configurations = self.create_configurations(organizations, users)
            self.stdout.write(self.style.SUCCESS(f'Created {len(configurations)} configurations'))

            # Create network devices
            network_devices = self.create_network_devices(organizations, locations, users)
            self.stdout.write(self.style.SUCCESS(f'Created {len(network_devices)} network devices'))

            # Create endpoint users
            endpoint_users = self.create_endpoint_users(organizations, locations, contacts, users)
            self.stdout.write(self.style.SUCCESS(f'Created {len(endpoint_users)} endpoint users'))

            # Create servers
            servers = self.create_servers(organizations, locations, users)
            self.stdout.write(self.style.SUCCESS(f'Created {len(servers)} servers'))

            # Create peripherals
            peripherals = self.create_peripherals(organizations, locations, users)
            self.stdout.write(self.style.SUCCESS(f'Created {len(peripherals)} peripherals'))

        self.stdout.write(self.style.SUCCESS('\nDummy data loaded successfully!'))
        self.stdout.write(self.style.SUCCESS('\nTest Users:'))
        self.stdout.write('  Superuser: admin@techvault.com / admin123')
        self.stdout.write('  User 1: john.doe@techvault.com / password123')
        self.stdout.write('  User 2: jane.smith@techvault.com / password123')

    def clear_data(self):
        """Clear all data from the database."""
        Peripheral.objects.all().delete()
        Server.objects.all().delete()
        EndpointUser.objects.all().delete()
        NetworkDevice.objects.all().delete()
        Configuration.objects.all().delete()
        PasswordEntry.objects.all().delete()
        Documentation.objects.all().delete()
        Contact.objects.all().delete()
        Location.objects.all().delete()
        Organization.objects.all().delete()
        User.objects.all().delete()

    def create_users(self):
        """Create test users."""
        users = []

        # Create superuser
        if not User.objects.filter(email='admin@techvault.com').exists():
            superuser = User.objects.create_superuser(
                email='admin@techvault.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            users.append(superuser)

        # Create regular users
        user_data = [
            {'email': 'john.doe@techvault.com', 'first_name': 'John', 'last_name': 'Doe'},
            {'email': 'jane.smith@techvault.com', 'first_name': 'Jane', 'last_name': 'Smith'},
            {'email': 'bob.johnson@techvault.com', 'first_name': 'Bob', 'last_name': 'Johnson'},
        ]

        for data in user_data:
            if not User.objects.filter(email=data['email']).exists():
                user = User.objects.create_user(
                    email=data['email'],
                    password='password123',
                    first_name=data['first_name'],
                    last_name=data['last_name']
                )
                users.append(user)

        return users

    def create_organizations(self, users):
        """Create organizations."""
        organizations_data = [
            {
                'name': 'Tech Solutions Inc',
                'description': 'Leading technology solutions provider',
                'website': 'https://techsolutions.example.com',
                'phone': '+1-555-0100',
                'email': 'info@techsolutions.example.com',
                'address': '123 Tech Boulevard',
                'city': 'San Francisco',
                'state_province': 'California',
                'postal_code': '94102',
                'country': 'United States',
            },
            {
                'name': 'Digital Innovations Ltd',
                'description': 'Innovative digital transformation company',
                'website': 'https://digitalinnovations.example.com',
                'phone': '+1-555-0200',
                'email': 'contact@digitalinnovations.example.com',
                'address': '456 Innovation Drive',
                'city': 'New York',
                'state_province': 'New York',
                'postal_code': '10001',
                'country': 'United States',
            },
            {
                'name': 'Cloud Systems Corp',
                'description': 'Cloud infrastructure and services provider',
                'website': 'https://cloudsystems.example.com',
                'phone': '+1-555-0300',
                'email': 'info@cloudsystems.example.com',
                'address': '789 Cloud Avenue',
                'city': 'Seattle',
                'state_province': 'Washington',
                'postal_code': '98101',
                'country': 'United States',
            },
        ]

        organizations = []
        for org_data in organizations_data:
            org, created = Organization.objects.get_or_create(
                name=org_data['name'],
                defaults={**org_data, 'created_by': random.choice(users)}
            )
            organizations.append(org)

        return organizations

    def create_locations(self, organizations, users):
        """Create locations for organizations."""
        locations = []

        locations_data = [
            # Tech Solutions Inc locations
            {
                'org_index': 0,
                'name': 'Headquarters',
                'description': 'Main office and data center',
                'address': '123 Tech Boulevard',
                'city': 'San Francisco',
                'state_province': 'California',
                'postal_code': '94102',
                'country': 'United States',
                'phone': '+1-555-0101',
            },
            {
                'org_index': 0,
                'name': 'West Coast Branch',
                'description': 'Regional office',
                'address': '555 Silicon Valley Road',
                'city': 'San Jose',
                'state_province': 'California',
                'postal_code': '95110',
                'country': 'United States',
                'phone': '+1-555-0102',
            },
            # Digital Innovations Ltd locations
            {
                'org_index': 1,
                'name': 'Main Office',
                'description': 'Corporate headquarters',
                'address': '456 Innovation Drive',
                'city': 'New York',
                'state_province': 'New York',
                'postal_code': '10001',
                'country': 'United States',
                'phone': '+1-555-0201',
            },
            # Cloud Systems Corp locations
            {
                'org_index': 2,
                'name': 'Data Center 1',
                'description': 'Primary data center facility',
                'address': '789 Cloud Avenue',
                'city': 'Seattle',
                'state_province': 'Washington',
                'postal_code': '98101',
                'country': 'United States',
                'phone': '+1-555-0301',
            },
        ]

        for loc_data in locations_data:
            org_index = loc_data.pop('org_index')
            location, created = Location.objects.get_or_create(
                organization=organizations[org_index],
                name=loc_data['name'],
                defaults={**loc_data, 'created_by': random.choice(users)}
            )
            locations.append(location)

        return locations

    def create_contacts(self, organizations, locations, users):
        """Create contacts for organizations."""
        contacts = []

        contacts_data = [
            {
                'org_index': 0,
                'location_index': 0,
                'first_name': 'Michael',
                'last_name': 'Anderson',
                'title': 'IT Manager',
                'email': 'michael.anderson@techsolutions.example.com',
                'phone': '+1-555-0110',
                'mobile': '+1-555-0111',
                'notes': 'Primary IT contact',
            },
            {
                'org_index': 0,
                'location_index': 1,
                'first_name': 'Sarah',
                'last_name': 'Williams',
                'title': 'Network Administrator',
                'email': 'sarah.williams@techsolutions.example.com',
                'phone': '+1-555-0112',
                'mobile': '+1-555-0113',
                'notes': 'Manages network infrastructure',
            },
            {
                'org_index': 1,
                'location_index': 2,
                'first_name': 'David',
                'last_name': 'Brown',
                'title': 'Systems Administrator',
                'email': 'david.brown@digitalinnovations.example.com',
                'phone': '+1-555-0210',
                'mobile': '+1-555-0211',
                'notes': 'Server and system management',
            },
            {
                'org_index': 2,
                'location_index': 3,
                'first_name': 'Emily',
                'last_name': 'Davis',
                'title': 'Cloud Architect',
                'email': 'emily.davis@cloudsystems.example.com',
                'phone': '+1-555-0310',
                'mobile': '+1-555-0311',
                'notes': 'Cloud infrastructure specialist',
            },
        ]

        for contact_data in contacts_data:
            org_index = contact_data.pop('org_index')
            location_index = contact_data.pop('location_index')
            contact, created = Contact.objects.get_or_create(
                organization=organizations[org_index],
                email=contact_data['email'],
                defaults={
                    **contact_data,
                    'location': locations[location_index] if location_index is not None else None,
                    'created_by': random.choice(users)
                }
            )
            contacts.append(contact)

        return contacts

    def create_documentations(self, organizations, users):
        """Create documentation entries."""
        documentations = []

        doc_data = [
            {
                'org_index': 0,
                'title': 'Network Configuration Guide',
                'content': 'This document outlines the standard network configuration procedures for all Tech Solutions Inc offices.\n\n## VLANs\n- VLAN 10: Management\n- VLAN 20: Workstations\n- VLAN 30: Servers\n- VLAN 40: Guest WiFi\n\n## IP Addressing\nAll networks use /24 subnets with the following scheme:\n10.x.y.0/24 where x is the site number and y is the VLAN number.',
                'category': 'configuration',
                'tags': 'network, vlans, ip-addressing, infrastructure',
                'is_published': True,
            },
            {
                'org_index': 0,
                'title': 'Backup and Recovery Procedure',
                'content': 'This procedure describes the backup and recovery process for critical systems.\n\n## Daily Backups\n1. All databases are backed up at 2 AM local time\n2. Incremental backups run every 4 hours\n3. Full backups run weekly on Sundays\n\n## Recovery\nIn case of data loss, follow these steps:\n1. Identify the backup point\n2. Notify management\n3. Begin restore process\n4. Verify data integrity',
                'category': 'procedure',
                'tags': 'backup, recovery, disaster-recovery, procedures',
                'is_published': True,
            },
            {
                'org_index': 1,
                'title': 'User Onboarding Checklist',
                'content': 'Complete checklist for onboarding new employees.\n\n## Hardware Setup\n- [ ] Assign laptop/desktop\n- [ ] Configure email account\n- [ ] Install required software\n- [ ] Set up VPN access\n\n## Access and Permissions\n- [ ] Create user accounts\n- [ ] Assign to appropriate groups\n- [ ] Configure file share access\n- [ ] Provide security training',
                'category': 'procedure',
                'tags': 'onboarding, hr, procedures, users',
                'is_published': True,
            },
            {
                'org_index': 1,
                'title': 'Security Policy',
                'content': 'Corporate security policy and guidelines.\n\n## Password Requirements\n- Minimum 12 characters\n- Must include uppercase, lowercase, numbers, and symbols\n- Changed every 90 days\n- No password reuse for last 5 passwords\n\n## Data Classification\n- Public: Can be shared freely\n- Internal: For employees only\n- Confidential: Requires manager approval\n- Restricted: Executive approval required',
                'category': 'policy',
                'tags': 'security, policy, passwords, data-classification',
                'is_published': True,
            },
            {
                'org_index': 2,
                'title': 'Cloud Migration Guide',
                'content': 'Step-by-step guide for migrating workloads to the cloud.\n\n## Pre-Migration\n1. Assess current infrastructure\n2. Identify dependencies\n3. Plan migration schedule\n4. Set up cloud environment\n\n## Migration Process\n1. Set up monitoring\n2. Migrate test workloads\n3. Validate functionality\n4. Migrate production workloads\n5. Update DNS records\n\n## Post-Migration\n1. Monitor performance\n2. Optimize costs\n3. Document changes\n4. Decommission old infrastructure',
                'category': 'guide',
                'tags': 'cloud, migration, procedures, infrastructure',
                'is_published': True,
            },
            {
                'org_index': 2,
                'title': 'Troubleshooting Network Issues',
                'content': 'Common network issues and their solutions.\n\n## No Internet Connectivity\n1. Check physical connections\n2. Verify IP configuration\n3. Test DNS resolution\n4. Check firewall rules\n5. Contact ISP if needed\n\n## Slow Performance\n1. Run speed test\n2. Check for bandwidth-heavy applications\n3. Verify QoS settings\n4. Check for network congestion\n5. Review logs for errors',
                'category': 'troubleshooting',
                'tags': 'network, troubleshooting, connectivity, performance',
                'is_published': True,
            },
        ]

        for doc in doc_data:
            org_index = doc.pop('org_index')
            documentation = Documentation.objects.create(
                organization=organizations[org_index],
                created_by=random.choice(users),
                **doc
            )
            documentations.append(documentation)

        return documentations

    def create_password_entries(self, organizations, users):
        """Create password vault entries."""
        password_entries = []

        passwords_data = [
            {
                'org_index': 0,
                'name': 'WiFi Admin Password',
                'username': 'admin',
                'password': 'WiFi_Admin_P@ssw0rd!',
                'url': 'https://192.168.1.1',
                'notes': 'Main office WiFi controller admin password',
                'category': 'device',
            },
            {
                'org_index': 0,
                'name': 'Firewall Admin',
                'username': 'admin',
                'password': 'Firewall_Secure_2024!',
                'url': 'https://firewall.techsolutions.local',
                'notes': 'Primary firewall administrator account',
                'category': 'device',
            },
            {
                'org_index': 0,
                'name': 'Database Admin',
                'username': 'db_admin',
                'password': 'DB_Admin_Str0ng!',
                'url': '',
                'notes': 'PostgreSQL database administrator password',
                'category': 'service',
            },
            {
                'org_index': 1,
                'name': 'AWS Root Account',
                'username': 'root@digitalinnovations.example.com',
                'password': 'AWS_Root_Secure_2024!',
                'url': 'https://aws.amazon.com',
                'notes': 'AWS root account credentials - use with caution',
                'category': 'account',
            },
            {
                'org_index': 1,
                'name': 'Office 365 Admin',
                'username': 'admin@digitalinnovations.onmicrosoft.com',
                'password': 'O365_Admin_P@ss!',
                'url': 'https://admin.microsoft.com',
                'notes': 'Office 365 global administrator account',
                'category': 'service',
            },
            {
                'org_index': 2,
                'name': 'Azure Portal Admin',
                'username': 'admin@cloudsystems.example.com',
                'password': 'Azure_Admin_2024!',
                'url': 'https://portal.azure.com',
                'notes': 'Azure subscription administrator',
                'category': 'account',
            },
            {
                'org_index': 2,
                'name': 'VMware vCenter',
                'username': 'administrator@vsphere.local',
                'password': 'vCenter_Admin_P@ss!',
                'url': 'https://vcenter.cloudsystems.local',
                'notes': 'VMware vCenter administrator credentials',
                'category': 'service',
            },
        ]

        for pwd_data in passwords_data:
            org_index = pwd_data.pop('org_index')
            password_entry = PasswordEntry.objects.create(
                organization=organizations[org_index],
                created_by=random.choice(users),
                **pwd_data
            )
            password_entries.append(password_entry)

        return password_entries

    def create_configurations(self, organizations, users):
        """Create configuration entries."""
        configurations = []

        config_data = [
            {
                'org_index': 0,
                'name': 'Primary Firewall Config',
                'config_type': 'security',
                'content': '''! Firewall Configuration
interface GigabitEthernet0/0
 description WAN Interface
 ip address dhcp
 no shutdown
!
interface GigabitEthernet0/1
 description LAN Interface
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
access-list 100 permit ip 192.168.1.0 0.0.0.255 any
access-list 100 deny ip any any''',
                'description': 'Main office firewall configuration',
                'version': '2.4.1',
            },
            {
                'org_index': 0,
                'name': 'Core Switch Configuration',
                'config_type': 'network',
                'content': '''! Core Switch Config
vlan 10
 name Management
vlan 20
 name Workstations
vlan 30
 name Servers
vlan 40
 name Guest_WiFi
!
interface GigabitEthernet1/0/1
 description Uplink to Firewall
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,40''',
                'description': 'Core switch VLAN configuration',
                'version': '15.2',
            },
            {
                'org_index': 1,
                'name': 'Web Server Nginx Config',
                'config_type': 'application',
                'content': '''server {
    listen 80;
    server_name digitalinnovations.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name digitalinnovations.example.com;

    ssl_certificate /etc/ssl/certs/server.crt;
    ssl_certificate_key /etc/ssl/private/server.key;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}''',
                'description': 'Nginx reverse proxy configuration',
                'version': '1.24.0',
            },
            {
                'org_index': 1,
                'name': 'Backup Script',
                'config_type': 'backup',
                'content': '''#!/bin/bash
# Daily backup script

BACKUP_DIR="/backups/daily"
DATE=$(date +%Y%m%d)

# Database backup
pg_dump -U postgres myapp > "$BACKUP_DIR/db_$DATE.sql"

# Files backup
tar -czf "$BACKUP_DIR/files_$DATE.tar.gz" /var/www/html

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -mtime +30 -delete

echo "Backup completed: $DATE"''',
                'description': 'Automated daily backup script',
                'version': '1.0',
            },
            {
                'org_index': 2,
                'name': 'Kubernetes Deployment',
                'config_type': 'application',
                'content': '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
      - name: webapp
        image: nginx:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "250m"
          limits:
            memory: "256Mi"
            cpu: "500m"''',
                'description': 'Kubernetes deployment configuration for web application',
                'version': '1.0',
            },
        ]

        for config in config_data:
            org_index = config.pop('org_index')
            configuration = Configuration.objects.create(
                organization=organizations[org_index],
                created_by=random.choice(users),
                **config
            )
            configurations.append(configuration)

        return configurations

    def create_network_devices(self, organizations, locations, users):
        """Create network devices."""
        network_devices = []

        devices_data = [
            {
                'org_index': 0,
                'location_index': 0,
                'name': 'Main Firewall',
                'device_type': 'firewall',
                'internet_provider': 'Comcast Business',
                'internet_speed': '1000/1000 Mbps',
                'manufacturer': 'Fortinet',
                'model': 'FortiGate 60F',
                'ip_address': '192.168.1.1',
                'mac_address': '00:09:0F:AA:BB:CC',
                'serial_number': 'FG60F-1234567890',
                'firmware_version': '7.2.4',
                'notes': 'Main office firewall with VPN capabilities',
            },
            {
                'org_index': 0,
                'location_index': 0,
                'name': 'Core Switch',
                'device_type': 'switch',
                'manufacturer': 'Cisco',
                'model': 'Catalyst 2960X-48TS-L',
                'ip_address': '192.168.1.2',
                'mac_address': '00:1A:2B:3C:4D:5E',
                'serial_number': 'FOC1234A5B6',
                'firmware_version': '15.2(7)E3',
                'notes': '48-port gigabit switch for main office',
            },
            {
                'org_index': 0,
                'location_index': 0,
                'name': 'Office WiFi AP-1',
                'device_type': 'wifi',
                'manufacturer': 'Ubiquiti',
                'model': 'UniFi AP AC Pro',
                'ip_address': '192.168.1.10',
                'mac_address': '00:11:22:33:44:55',
                'serial_number': 'UBNT-1234567890',
                'firmware_version': '6.2.41',
                'notes': 'WiFi access point for floor 1',
            },
            {
                'org_index': 0,
                'location_index': 1,
                'name': 'Branch Router',
                'device_type': 'router',
                'internet_provider': 'AT&T Fiber',
                'internet_speed': '500/500 Mbps',
                'manufacturer': 'Cisco',
                'model': 'ISR 4331',
                'ip_address': '192.168.2.1',
                'mac_address': '00:AA:BB:CC:DD:EE',
                'serial_number': 'FDO12345678',
                'firmware_version': '16.12.04',
                'notes': 'West Coast branch office router',
            },
            {
                'org_index': 1,
                'location_index': 2,
                'name': 'Main Firewall/Router',
                'device_type': 'firewall_router',
                'internet_provider': 'Verizon FiOS',
                'internet_speed': '940/880 Mbps',
                'manufacturer': 'Palo Alto Networks',
                'model': 'PA-220',
                'ip_address': '10.0.0.1',
                'mac_address': '00:1B:17:AA:BB:CC',
                'serial_number': 'PA220-1234567',
                'firmware_version': '10.2.3',
                'notes': 'Combined firewall and router for main office',
            },
            {
                'org_index': 2,
                'location_index': 3,
                'name': 'Datacenter Core Switch',
                'device_type': 'switch',
                'manufacturer': 'Arista',
                'model': '7050SX3-48YC12',
                'ip_address': '10.1.1.1',
                'mac_address': '44:4C:A8:AA:BB:CC',
                'serial_number': 'JPE12345678',
                'firmware_version': '4.28.3M',
                'notes': 'High-performance datacenter switch',
            },
        ]

        for device_data in devices_data:
            org_index = device_data.pop('org_index')
            location_index = device_data.pop('location_index')
            network_device = NetworkDevice.objects.create(
                organization=organizations[org_index],
                location=locations[location_index] if location_index is not None else None,
                created_by=random.choice(users),
                **device_data
            )
            network_devices.append(network_device)

        return network_devices

    def create_endpoint_users(self, organizations, locations, contacts, users):
        """Create endpoint user devices."""
        endpoint_users = []

        endpoints_data = [
            {
                'org_index': 0,
                'location_index': 0,
                'contact_index': 0,
                'name': 'DESK-MANDERSON',
                'device_type': 'desktop',
                'manufacturer': 'Dell',
                'model': 'OptiPlex 7090',
                'cpu': 'Intel Core i7-11700 @ 2.50GHz',
                'ram': '32GB DDR4',
                'storage': '1TB NVMe SSD',
                'gpu': 'Intel UHD Graphics 750',
                'operating_system': 'Windows 11 Pro',
                'software_installed': 'Microsoft Office 365, Chrome, Zoom, Slack, Visual Studio Code',
                'ip_address': '192.168.1.100',
                'mac_address': '00:11:22:AA:BB:01',
                'hostname': 'DESK-MANDERSON',
                'serial_number': 'DL123456',
                'purchase_date': (timezone.now() - timedelta(days=365)).date(),
                'warranty_expiry': (timezone.now() + timedelta(days=730)).date(),
                'notes': 'IT Manager workstation',
            },
            {
                'org_index': 0,
                'location_index': 1,
                'contact_index': 1,
                'name': 'LAPTOP-SWILLIAMS',
                'device_type': 'laptop',
                'manufacturer': 'Lenovo',
                'model': 'ThinkPad X1 Carbon Gen 9',
                'cpu': 'Intel Core i7-1185G7 @ 3.00GHz',
                'ram': '16GB LPDDR4',
                'storage': '512GB NVMe SSD',
                'gpu': 'Intel Iris Xe Graphics',
                'operating_system': 'Windows 11 Pro',
                'software_installed': 'Microsoft Office 365, Chrome, PuTTY, WinSCP, Wireshark',
                'ip_address': '192.168.2.50',
                'mac_address': '00:11:22:AA:BB:02',
                'hostname': 'LAPTOP-SWILLIAMS',
                'serial_number': 'LN789012',
                'purchase_date': (timezone.now() - timedelta(days=180)).date(),
                'warranty_expiry': (timezone.now() + timedelta(days=915)).date(),
                'notes': 'Network Administrator laptop',
            },
            {
                'org_index': 1,
                'location_index': 2,
                'contact_index': 2,
                'name': 'WORK-DBROWN',
                'device_type': 'workstation',
                'manufacturer': 'HP',
                'model': 'Z2 G9 Tower',
                'cpu': 'Intel Xeon W-1390 @ 2.80GHz',
                'ram': '64GB DDR4 ECC',
                'storage': '2TB NVMe SSD + 4TB HDD',
                'gpu': 'NVIDIA RTX A2000',
                'operating_system': 'Ubuntu 22.04 LTS',
                'software_installed': 'Docker, Kubernetes, Ansible, Terraform, VS Code, IntelliJ IDEA',
                'ip_address': '10.0.1.100',
                'mac_address': '00:11:22:AA:BB:03',
                'hostname': 'WORK-DBROWN',
                'serial_number': 'HP345678',
                'purchase_date': (timezone.now() - timedelta(days=90)).date(),
                'warranty_expiry': (timezone.now() + timedelta(days=1005)).date(),
                'notes': 'Systems Administrator workstation',
            },
            {
                'org_index': 2,
                'location_index': 3,
                'contact_index': 3,
                'name': 'LAPTOP-EDAVIS',
                'device_type': 'laptop',
                'manufacturer': 'Apple',
                'model': 'MacBook Pro 16" M2 Max',
                'cpu': 'Apple M2 Max (12-core CPU)',
                'ram': '64GB Unified Memory',
                'storage': '2TB SSD',
                'gpu': 'Apple M2 Max (38-core GPU)',
                'operating_system': 'macOS Ventura 13.5',
                'software_installed': 'Xcode, Docker, Terraform, AWS CLI, Azure CLI, VS Code',
                'ip_address': '10.1.2.50',
                'mac_address': '00:11:22:AA:BB:04',
                'hostname': 'LAPTOP-EDAVIS',
                'serial_number': 'AP901234',
                'purchase_date': (timezone.now() - timedelta(days=60)).date(),
                'warranty_expiry': (timezone.now() + timedelta(days=1035)).date(),
                'notes': 'Cloud Architect laptop',
            },
        ]

        for endpoint_data in endpoints_data:
            org_index = endpoint_data.pop('org_index')
            location_index = endpoint_data.pop('location_index')
            contact_index = endpoint_data.pop('contact_index')
            endpoint_user = EndpointUser.objects.create(
                organization=organizations[org_index],
                location=locations[location_index] if location_index is not None else None,
                assigned_to=contacts[contact_index] if contact_index is not None else None,
                created_by=random.choice(users),
                **endpoint_data
            )
            endpoint_users.append(endpoint_user)

        return endpoint_users

    def create_servers(self, organizations, locations, users):
        """Create servers."""
        servers = []

        servers_data = [
            {
                'org_index': 0,
                'location_index': 0,
                'name': 'SRV-WEB-01',
                'server_type': 'physical',
                'role': 'Web Server',
                'manufacturer': 'Dell',
                'model': 'PowerEdge R640',
                'cpu': '2x Intel Xeon Silver 4214R @ 2.40GHz (24 cores total)',
                'ram': '128GB DDR4 ECC',
                'storage': '4x 1TB SSD RAID 10',
                'operating_system': 'Ubuntu Server 22.04 LTS',
                'software_installed': 'Nginx, PHP 8.2, MySQL 8.0, Redis',
                'ip_address': '192.168.1.50',
                'mac_address': '00:1A:2B:3C:4D:50',
                'hostname': 'srv-web-01.techsolutions.local',
                'serial_number': 'DPSRV123456',
                'notes': 'Primary web server for corporate applications',
            },
            {
                'org_index': 0,
                'location_index': 0,
                'name': 'SRV-DB-01',
                'server_type': 'physical',
                'role': 'Database Server',
                'manufacturer': 'HPE',
                'model': 'ProLiant DL380 Gen10',
                'cpu': '2x Intel Xeon Gold 6230R @ 2.10GHz (52 cores total)',
                'ram': '256GB DDR4 ECC',
                'storage': '8x 2TB SSD RAID 10',
                'operating_system': 'Red Hat Enterprise Linux 8.7',
                'software_installed': 'PostgreSQL 15, MySQL 8.0, MongoDB 6.0',
                'ip_address': '192.168.1.51',
                'mac_address': '00:1A:2B:3C:4D:51',
                'hostname': 'srv-db-01.techsolutions.local',
                'serial_number': 'HPSRV789012',
                'notes': 'Primary database server',
            },
            {
                'org_index': 0,
                'location_index': 0,
                'name': 'VM-APP-01',
                'server_type': 'virtual',
                'role': 'Application Server',
                'manufacturer': 'VMware',
                'model': 'Virtual Machine',
                'cpu': '8 vCPUs',
                'ram': '32GB',
                'storage': '500GB vDisk',
                'operating_system': 'Windows Server 2022',
                'software_installed': 'IIS, .NET Framework 4.8, SQL Server Client Tools',
                'ip_address': '192.168.1.52',
                'mac_address': '00:50:56:AA:BB:01',
                'hostname': 'vm-app-01.techsolutions.local',
                'serial_number': 'VMware-42 15 6d e4 5a 3f',
                'notes': 'Virtual machine running business applications',
            },
            {
                'org_index': 1,
                'location_index': 2,
                'name': 'SRV-FILE-01',
                'server_type': 'physical',
                'role': 'File Server',
                'manufacturer': 'Synology',
                'model': 'RS2421+',
                'cpu': 'Intel Xeon D-1531 @ 2.20GHz',
                'ram': '16GB DDR4 ECC',
                'storage': '12x 8TB HDD RAID 6',
                'operating_system': 'DSM 7.2',
                'software_installed': 'SMB, NFS, iSCSI Target, Snapshot Replication',
                'ip_address': '10.0.1.50',
                'mac_address': '00:11:32:AA:BB:C0',
                'hostname': 'srv-file-01.digitalinnovations.local',
                'serial_number': 'SYN123456789',
                'notes': 'Network attached storage for file sharing',
            },
            {
                'org_index': 2,
                'location_index': 3,
                'name': 'AWS-WEB-PROD',
                'server_type': 'cloud',
                'role': 'Web Server',
                'manufacturer': 'AWS',
                'model': 'EC2 c5.2xlarge',
                'cpu': '8 vCPUs (Intel Xeon Platinum 8275CL)',
                'ram': '16GB',
                'storage': '100GB gp3 SSD',
                'operating_system': 'Amazon Linux 2023',
                'software_installed': 'Docker, Nginx, Node.js 18, PM2',
                'ip_address': '10.1.10.50',
                'hostname': 'aws-web-prod.cloudsystems.local',
                'notes': 'Production web server on AWS - us-east-1',
            },
            {
                'org_index': 2,
                'location_index': 3,
                'name': 'K8S-NODE-01',
                'server_type': 'container',
                'role': 'Kubernetes Worker Node',
                'manufacturer': 'Azure',
                'model': 'AKS Standard_D4s_v3',
                'cpu': '4 vCPUs',
                'ram': '16GB',
                'storage': '128GB Premium SSD',
                'operating_system': 'Ubuntu 22.04 (AKS-optimized)',
                'software_installed': 'Kubernetes 1.28, containerd, Azure CNI',
                'ip_address': '10.1.20.10',
                'hostname': 'k8s-node-01',
                'notes': 'Kubernetes worker node in Azure AKS cluster',
            },
        ]

        for server_data in servers_data:
            org_index = server_data.pop('org_index')
            location_index = server_data.pop('location_index', None)
            server = Server.objects.create(
                organization=organizations[org_index],
                location=locations[location_index] if location_index is not None else None,
                created_by=random.choice(users),
                **server_data
            )
            servers.append(server)

        return servers

    def create_peripherals(self, organizations, locations, users):
        """Create peripheral devices."""
        peripherals = []

        peripherals_data = [
            {
                'org_index': 0,
                'location_index': 0,
                'name': 'Office Printer 1',
                'device_type': 'multifunction',
                'manufacturer': 'HP',
                'model': 'LaserJet Enterprise MFP M528dn',
                'ip_address': '192.168.1.200',
                'mac_address': '00:1A:4B:AA:BB:01',
                'serial_number': 'HPPRT123456',
                'notes': 'Main office multifunction printer - Floor 1',
            },
            {
                'org_index': 0,
                'location_index': 0,
                'name': 'Office Printer 2',
                'device_type': 'printer',
                'manufacturer': 'Canon',
                'model': 'imageRUNNER ADVANCE C5550i',
                'ip_address': '192.168.1.201',
                'mac_address': '00:1A:4B:AA:BB:02',
                'serial_number': 'CANPRT789012',
                'notes': 'Color printer for marketing department - Floor 2',
            },
            {
                'org_index': 0,
                'location_index': 0,
                'name': 'Server Room UPS',
                'device_type': 'ups',
                'manufacturer': 'APC',
                'model': 'Smart-UPS 3000VA LCD',
                'ip_address': '192.168.1.210',
                'mac_address': '00:C0:B7:AA:BB:01',
                'serial_number': 'APCUPS345678',
                'notes': 'Battery backup for server room - 2 hour runtime',
            },
            {
                'org_index': 0,
                'location_index': 1,
                'name': 'Branch Scanner',
                'device_type': 'scanner',
                'manufacturer': 'Fujitsu',
                'model': 'fi-7160',
                'ip_address': '192.168.2.200',
                'mac_address': '00:1B:4C:AA:BB:03',
                'serial_number': 'FUJSCAN901234',
                'notes': 'Document scanner for West Coast branch',
            },
            {
                'org_index': 1,
                'location_index': 2,
                'name': 'Office NAS',
                'device_type': 'nas',
                'manufacturer': 'QNAP',
                'model': 'TS-473A',
                'ip_address': '10.0.1.210',
                'mac_address': '00:08:9B:AA:BB:04',
                'serial_number': 'QNAPNAS567890',
                'notes': 'Network storage for department file shares - 16TB total',
            },
            {
                'org_index': 2,
                'location_index': 3,
                'name': 'Datacenter UPS Primary',
                'device_type': 'ups',
                'manufacturer': 'Eaton',
                'model': '9PX 8000VA',
                'ip_address': '10.1.1.210',
                'mac_address': '00:C0:B7:AA:BB:05',
                'serial_number': 'EATONUPS123456',
                'notes': 'Primary UPS for datacenter - 8KVA',
            },
        ]

        for peripheral_data in peripherals_data:
            org_index = peripheral_data.pop('org_index')
            location_index = peripheral_data.pop('location_index')
            peripheral = Peripheral.objects.create(
                organization=organizations[org_index],
                location=locations[location_index] if location_index is not None else None,
                created_by=random.choice(users),
                **peripheral_data
            )
            peripherals.append(peripheral)

        return peripherals
