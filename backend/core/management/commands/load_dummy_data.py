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
    Configuration, NetworkDevice, EndpointUser, Server, Peripheral,
    Software, Backup
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

            # Create software
            software = self.create_software(organizations, contacts, users)
            self.stdout.write(self.style.SUCCESS(f'Created {len(software)} software entries'))

            # Create backups
            backups = self.create_backups(organizations, locations, servers, users)
            self.stdout.write(self.style.SUCCESS(f'Created {len(backups)} backup entries'))

        self.stdout.write(self.style.SUCCESS('\nDummy data loaded successfully!'))
        self.stdout.write(self.style.SUCCESS('\nTest Users:'))
        self.stdout.write('  Superuser: admin@techvault.com / admin123')
        self.stdout.write('  User 1: john.doe@techvault.com / password123')
        self.stdout.write('  User 2: jane.smith@techvault.com / password123')

    def clear_data(self):
        """Clear all data from the database."""
        Backup.objects.all().delete()
        Software.objects.all().delete()
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
            {
                'name': 'TechGuard MSP',
                'description': 'Managed Service Provider offering comprehensive IT support and infrastructure management',
                'website': 'https://techguardmsp.example.com',
                'phone': '+1-555-0400',
                'email': 'support@techguardmsp.example.com',
                'address': '250 MSP Plaza',
                'city': 'Austin',
                'state_province': 'Texas',
                'postal_code': '78701',
                'country': 'United States',
            },
            {
                'name': 'Acme Manufacturing Co',
                'description': 'Small manufacturing business specializing in industrial components',
                'website': 'https://acmemfg.example.com',
                'phone': '+1-555-0500',
                'email': 'info@acmemfg.example.com',
                'address': '789 Industrial Park Drive',
                'city': 'Chicago',
                'state_province': 'Illinois',
                'postal_code': '60601',
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
            # TechGuard MSP locations
            {
                'org_index': 3,
                'name': 'MSP Headquarters',
                'description': 'Main office and NOC (Network Operations Center)',
                'address': '250 MSP Plaza',
                'city': 'Austin',
                'state_province': 'Texas',
                'postal_code': '78701',
                'country': 'United States',
                'phone': '+1-555-0401',
            },
            {
                'org_index': 3,
                'name': 'Remote Support Center',
                'description': '24/7 Remote support and monitoring facility',
                'address': '500 Tech Support Lane',
                'city': 'Dallas',
                'state_province': 'Texas',
                'postal_code': '75201',
                'country': 'United States',
                'phone': '+1-555-0402',
            },
            # Acme Manufacturing Co locations
            {
                'org_index': 4,
                'name': 'Main Office',
                'description': 'Corporate office and manufacturing facility',
                'address': '789 Industrial Park Drive',
                'city': 'Chicago',
                'state_province': 'Illinois',
                'postal_code': '60601',
                'country': 'United States',
                'phone': '+1-555-0501',
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
            # TechGuard MSP contacts
            {
                'org_index': 3,
                'location_index': 4,
                'first_name': 'Robert',
                'last_name': 'Miller',
                'title': 'MSP Operations Manager',
                'email': 'robert.miller@techguardmsp.example.com',
                'phone': '+1-555-0410',
                'mobile': '+1-555-0411',
                'notes': 'Manages day-to-day MSP operations and client accounts',
            },
            {
                'org_index': 3,
                'location_index': 4,
                'first_name': 'Jennifer',
                'last_name': 'Taylor',
                'title': 'Senior Network Engineer',
                'email': 'jennifer.taylor@techguardmsp.example.com',
                'phone': '+1-555-0412',
                'mobile': '+1-555-0413',
                'notes': 'Lead network engineer for client infrastructure',
            },
            {
                'org_index': 3,
                'location_index': 5,
                'first_name': 'Kevin',
                'last_name': 'Martinez',
                'title': 'NOC Supervisor',
                'email': 'kevin.martinez@techguardmsp.example.com',
                'phone': '+1-555-0414',
                'mobile': '+1-555-0415',
                'notes': 'Supervises network operations center team',
            },
            # Acme Manufacturing Co contacts (SMB with 25 employees)
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'James',
                'last_name': 'Richardson',
                'title': 'CEO',
                'email': 'james.richardson@acmemfg.example.com',
                'phone': '+1-555-0510',
                'mobile': '+1-555-0511',
                'notes': 'Company CEO and founder',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Patricia',
                'last_name': 'Cooper',
                'title': 'CFO',
                'email': 'patricia.cooper@acmemfg.example.com',
                'phone': '+1-555-0512',
                'mobile': '+1-555-0513',
                'notes': 'Chief Financial Officer',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Thomas',
                'last_name': 'Bennett',
                'title': 'IT Manager',
                'email': 'thomas.bennett@acmemfg.example.com',
                'phone': '+1-555-0514',
                'mobile': '+1-555-0515',
                'notes': 'Manages all IT infrastructure and staff',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Linda',
                'last_name': 'Morgan',
                'title': 'Office Manager',
                'email': 'linda.morgan@acmemfg.example.com',
                'phone': '+1-555-0516',
                'mobile': '+1-555-0517',
                'notes': 'Manages office operations and HR',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Richard',
                'last_name': 'Powell',
                'title': 'Sales Manager',
                'email': 'richard.powell@acmemfg.example.com',
                'phone': '+1-555-0518',
                'mobile': '+1-555-0519',
                'notes': 'Leads sales team',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Nancy',
                'last_name': 'Hughes',
                'title': 'Production Manager',
                'email': 'nancy.hughes@acmemfg.example.com',
                'phone': '+1-555-0520',
                'mobile': '+1-555-0521',
                'notes': 'Oversees manufacturing operations',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Christopher',
                'last_name': 'Watson',
                'title': 'Quality Control Manager',
                'email': 'christopher.watson@acmemfg.example.com',
                'phone': '+1-555-0522',
                'mobile': '+1-555-0523',
                'notes': 'Manages quality assurance processes',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Karen',
                'last_name': 'Brooks',
                'title': 'Purchasing Agent',
                'email': 'karen.brooks@acmemfg.example.com',
                'phone': '+1-555-0524',
                'mobile': '+1-555-0525',
                'notes': 'Handles procurement and vendor relations',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Daniel',
                'last_name': 'Sanders',
                'title': 'Sales Representative',
                'email': 'daniel.sanders@acmemfg.example.com',
                'phone': '+1-555-0526',
                'mobile': '+1-555-0527',
                'notes': 'Outside sales representative',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Betty',
                'last_name': 'Price',
                'title': 'Accountant',
                'email': 'betty.price@acmemfg.example.com',
                'phone': '+1-555-0528',
                'mobile': '+1-555-0529',
                'notes': 'Manages accounts payable and receivable',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Matthew',
                'last_name': 'Reed',
                'title': 'Production Supervisor',
                'email': 'matthew.reed@acmemfg.example.com',
                'phone': '+1-555-0530',
                'mobile': '+1-555-0531',
                'notes': 'Supervises production floor',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Helen',
                'last_name': 'Coleman',
                'title': 'HR Coordinator',
                'email': 'helen.coleman@acmemfg.example.com',
                'phone': '+1-555-0532',
                'mobile': '+1-555-0533',
                'notes': 'Human resources and payroll',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Donald',
                'last_name': 'Butler',
                'title': 'Maintenance Technician',
                'email': 'donald.butler@acmemfg.example.com',
                'phone': '+1-555-0534',
                'mobile': '+1-555-0535',
                'notes': 'Maintains equipment and facilities',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Sandra',
                'last_name': 'Jenkins',
                'title': 'Customer Service Representative',
                'email': 'sandra.jenkins@acmemfg.example.com',
                'phone': '+1-555-0536',
                'mobile': '+1-555-0537',
                'notes': 'Handles customer inquiries and orders',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'George',
                'last_name': 'Foster',
                'title': 'Warehouse Manager',
                'email': 'george.foster@acmemfg.example.com',
                'phone': '+1-555-0538',
                'mobile': '+1-555-0539',
                'notes': 'Manages inventory and shipping',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Ashley',
                'last_name': 'Ross',
                'title': 'Marketing Coordinator',
                'email': 'ashley.ross@acmemfg.example.com',
                'phone': '+1-555-0540',
                'mobile': '+1-555-0541',
                'notes': 'Manages marketing campaigns and website',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Steven',
                'last_name': 'Perry',
                'title': 'Senior Machinist',
                'email': 'steven.perry@acmemfg.example.com',
                'phone': '+1-555-0542',
                'mobile': '+1-555-0543',
                'notes': 'Operates CNC machines',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Donna',
                'last_name': 'Howard',
                'title': 'Shipping Coordinator',
                'email': 'donna.howard@acmemfg.example.com',
                'phone': '+1-555-0544',
                'mobile': '+1-555-0545',
                'notes': 'Coordinates outbound shipments',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Paul',
                'last_name': 'Long',
                'title': 'Quality Inspector',
                'email': 'paul.long@acmemfg.example.com',
                'phone': '+1-555-0546',
                'mobile': '+1-555-0547',
                'notes': 'Inspects finished products',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Carol',
                'last_name': 'Patterson',
                'title': 'Receptionist',
                'email': 'carol.patterson@acmemfg.example.com',
                'phone': '+1-555-0548',
                'mobile': '+1-555-0549',
                'notes': 'Front desk and phone support',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Ryan',
                'last_name': 'Barnes',
                'title': 'Assembly Technician',
                'email': 'ryan.barnes@acmemfg.example.com',
                'phone': '+1-555-0550',
                'mobile': '+1-555-0551',
                'notes': 'Assembles component parts',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Michelle',
                'last_name': 'Simmons',
                'title': 'Production Operator',
                'email': 'michelle.simmons@acmemfg.example.com',
                'phone': '+1-555-0552',
                'mobile': '+1-555-0553',
                'notes': 'Machine operator',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Jason',
                'last_name': 'Kelly',
                'title': 'Inventory Clerk',
                'email': 'jason.kelly@acmemfg.example.com',
                'phone': '+1-555-0554',
                'mobile': '+1-555-0555',
                'notes': 'Tracks inventory levels',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Laura',
                'last_name': 'Ward',
                'title': 'Design Engineer',
                'email': 'laura.ward@acmemfg.example.com',
                'phone': '+1-555-0556',
                'mobile': '+1-555-0557',
                'notes': 'Product design and CAD work',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'first_name': 'Brian',
                'last_name': 'Torres',
                'title': 'Facilities Coordinator',
                'email': 'brian.torres@acmemfg.example.com',
                'phone': '+1-555-0558',
                'mobile': '+1-555-0559',
                'notes': 'Building maintenance and security',
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
            # TechGuard MSP Documentation
            {
                'org_index': 3,
                'title': 'MSP Client Onboarding Process',
                'content': 'Standard procedure for onboarding new MSP clients.\n\n## Initial Assessment\n1. Conduct IT infrastructure audit\n2. Document all hardware and software\n3. Identify security vulnerabilities\n4. Review backup procedures\n\n## Setup\n1. Deploy monitoring agents\n2. Configure RMM tools\n3. Set up remote access\n4. Implement backup solution\n5. Configure ticketing system\n\n## Documentation\n1. Create network diagram\n2. Document all credentials\n3. Create runbook for common issues\n4. Establish SLA and escalation procedures',
                'category': 'procedure',
                'tags': 'msp, onboarding, clients, procedures',
                'is_published': True,
            },
            {
                'org_index': 3,
                'title': 'MSP Service Level Agreement',
                'content': 'Standard SLA for managed service clients.\n\n## Response Times\n- Critical (P1): 1 hour\n- High (P2): 4 hours\n- Medium (P3): 8 hours\n- Low (P4): 24 hours\n\n## Services Included\n- 24/7 monitoring\n- Remote support\n- Patch management\n- Backup management\n- Security monitoring\n- Monthly reporting\n\n## Exclusions\n- On-site visits (separate fee)\n- Hardware purchases\n- Software licensing\n- Custom development',
                'category': 'policy',
                'tags': 'msp, sla, service-level, policy',
                'is_published': True,
            },
            # Acme Manufacturing Documentation
            {
                'org_index': 4,
                'title': 'Employee IT Usage Policy',
                'content': 'Acceptable use policy for company IT resources.\n\n## General Rules\n- Company devices for business use only\n- No unauthorized software installations\n- Report security incidents immediately\n- Use strong passwords\n\n## Email Guidelines\n- Professional communication only\n- No mass forwarding\n- Be cautious of phishing attempts\n- Company email is monitored\n\n## Internet Access\n- Allowed for work-related purposes\n- No streaming services during work hours\n- Social media limited to breaks\n- Downloading requires approval',
                'category': 'policy',
                'tags': 'policy, acceptable-use, employees, security',
                'is_published': True,
            },
            {
                'org_index': 4,
                'title': 'Network and WiFi Setup',
                'content': 'Network configuration for Acme Manufacturing.\n\n## Office Network\n- Network: 10.50.0.0/24\n- Gateway: 10.50.0.1\n- DNS: 10.50.0.10, 8.8.8.8\n- DHCP Range: 10.50.0.100-10.50.0.200\n\n## WiFi Networks\n- Staff WiFi: AcmeMfg-Staff (WPA3)\n- Guest WiFi: AcmeMfg-Guest (Isolated)\n- Production WiFi: AcmeMfg-Production (IoT devices)\n\n## VLANs\n- VLAN 10: Management\n- VLAN 20: Office\n- VLAN 30: Production Floor\n- VLAN 40: Guest',
                'category': 'configuration',
                'tags': 'network, wifi, configuration, infrastructure',
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
            # TechGuard MSP passwords
            {
                'org_index': 3,
                'name': 'RMM Platform Admin',
                'username': 'admin@techguardmsp',
                'password': 'RMM_Secure_2024!',
                'url': 'https://rmm.techguardmsp.example.com',
                'notes': 'Remote monitoring and management platform admin',
                'category': 'service',
            },
            {
                'org_index': 3,
                'name': 'PSA Ticketing System',
                'username': 'admin',
                'password': 'PSA_Admin_P@ss!',
                'url': 'https://tickets.techguardmsp.example.com',
                'notes': 'Professional Services Automation admin account',
                'category': 'service',
            },
            {
                'org_index': 3,
                'name': 'Backup Management Console',
                'username': 'msp_admin',
                'password': 'Backup_Mgmt_2024!',
                'url': 'https://backup.techguardmsp.example.com',
                'notes': 'Centralized backup management for all clients',
                'category': 'service',
            },
            # Acme Manufacturing passwords
            {
                'org_index': 4,
                'name': 'Firewall Admin',
                'username': 'admin',
                'password': 'Acme_FW_2024!',
                'url': 'https://10.50.0.1',
                'notes': 'Main office firewall admin account',
                'category': 'device',
            },
            {
                'org_index': 4,
                'name': 'Server Administrator',
                'username': 'administrator',
                'password': 'Acme_SrvAdmin_2024!',
                'url': '',
                'notes': 'Windows Server local administrator password',
                'category': 'device',
            },
            {
                'org_index': 4,
                'name': 'Office 365 Admin',
                'username': 'admin@acmemfg.onmicrosoft.com',
                'password': 'O365_Acme_Admin!',
                'url': 'https://admin.microsoft.com',
                'notes': 'Microsoft 365 global administrator',
                'category': 'account',
            },
            {
                'org_index': 4,
                'name': 'Accounting Software',
                'username': 'admin',
                'password': 'QuickBooks_2024!',
                'url': '',
                'notes': 'QuickBooks administrator account',
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
            # TechGuard MSP configurations
            {
                'org_index': 3,
                'name': 'RMM Monitoring Policies',
                'config_type': 'application',
                'content': '''# MSP Monitoring Configuration
## Disk Space Monitoring
- Warning: < 20% free
- Critical: < 10% free
- Check interval: 30 minutes

## CPU Monitoring
- Warning: > 80% for 10 minutes
- Critical: > 95% for 5 minutes
- Check interval: 5 minutes

## Memory Monitoring
- Warning: > 85% usage
- Critical: > 95% usage
- Check interval: 5 minutes

## Service Monitoring
- Check critical services every 2 minutes
- Alert on service failure
- Auto-restart if configured

## Patch Management
- Check for patches daily
- Test patches in lab environment
- Deploy to clients within 7 days of release
- Critical patches within 24 hours''',
                'description': 'Standard RMM monitoring policies for client systems',
                'version': '2.1',
            },
            {
                'org_index': 3,
                'name': 'Client Backup Policy',
                'config_type': 'backup',
                'content': '''# MSP Client Backup Standard

## Backup Schedule
- Workstations: Daily incremental, Weekly full
- Servers: Hourly incremental, Daily full
- Databases: Every 4 hours
- Retention: 30 days online, 1 year archive

## Backup Verification
- Daily backup success reports
- Weekly restore tests
- Monthly full recovery drill

## Backup Storage
- Primary: On-site NAS
- Secondary: Cloud backup (encrypted)
- Archive: Offsite tape storage''',
                'description': 'Standard backup policy for MSP clients',
                'version': '1.5',
            },
            # Acme Manufacturing configurations
            {
                'org_index': 4,
                'name': 'Office Firewall Rules',
                'config_type': 'security',
                'content': '''# Firewall Configuration for Acme Manufacturing

## WAN Rules
- Allow: HTTP/HTTPS outbound
- Allow: DNS outbound
- Allow: Email (SMTP/IMAP) outbound
- Block: All other outbound
- Block: All inbound except VPN

## LAN Rules
- VLAN 20 (Office) -> Internet: Allow
- VLAN 30 (Production) -> Internet: Limited
- VLAN 40 (Guest) -> LAN: Deny
- VLAN 40 (Guest) -> Internet: Allow HTTP/HTTPS only

## Port Forwarding
- RDP: External IP:3389 -> 10.50.0.10:3389 (VPN only)
- HTTPS: External IP:443 -> 10.50.0.20:443''',
                'description': 'Firewall rules and policies',
                'version': '1.2',
            },
            {
                'org_index': 4,
                'name': 'Windows Server Backup',
                'config_type': 'backup',
                'content': '''@echo off
REM Daily backup script for Windows Server

SET BACKUP_DIR=E:\\Backups
SET DATE=%date:~-4,4%%date:~-10,2%%date:~-7,2%

REM Backup System State
wbadmin start systemstatebackup -backupTarget:%BACKUP_DIR% -quiet

REM Backup SQL Databases
sqlcmd -Q "BACKUP DATABASE [CompanyDB] TO DISK='%BACKUP_DIR%\\CompanyDB_%DATE%.bak'"

REM Backup file shares
robocopy "D:\\Shares" "%BACKUP_DIR%\\Shares_%DATE%" /MIR /R:3 /W:5

REM Delete backups older than 30 days
forfiles /p %BACKUP_DIR% /m *.bak /d -30 /c "cmd /c del @path"

echo Backup completed: %DATE%''',
                'description': 'Daily Windows Server backup script',
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
            # TechGuard MSP network devices
            {
                'org_index': 3,
                'location_index': 4,
                'name': 'MSP Office Firewall',
                'device_type': 'firewall',
                'internet_provider': 'AT&T Business Fiber',
                'internet_speed': '1000/1000 Mbps',
                'manufacturer': 'Fortinet',
                'model': 'FortiGate 100F',
                'ip_address': '192.168.100.1',
                'mac_address': '00:09:0F:CC:DD:EE',
                'serial_number': 'FG100F-MSP001',
                'firmware_version': '7.2.5',
                'notes': 'Main office firewall with VPN for remote workers',
            },
            {
                'org_index': 3,
                'location_index': 4,
                'name': 'MSP Core Switch',
                'device_type': 'switch',
                'manufacturer': 'Cisco',
                'model': 'Catalyst 2960X-24TS',
                'ip_address': '192.168.100.2',
                'mac_address': '00:1A:2B:CC:DD:EE',
                'serial_number': 'FOC-MSP-001',
                'firmware_version': '15.2(7)E4',
                'notes': '24-port managed switch for MSP office',
            },
            {
                'org_index': 3,
                'location_index': 4,
                'name': 'MSP WiFi Controller',
                'device_type': 'wifi',
                'manufacturer': 'Ubiquiti',
                'model': 'UniFi Dream Machine Pro',
                'ip_address': '192.168.100.10',
                'mac_address': '00:11:22:CC:DD:EE',
                'serial_number': 'UDMP-MSP-001',
                'firmware_version': '7.5.176',
                'notes': 'Manages all WiFi access points',
            },
            # Acme Manufacturing network devices
            {
                'org_index': 4,
                'location_index': 6,
                'name': 'Main Firewall',
                'device_type': 'firewall_router',
                'internet_provider': 'Comcast Business',
                'internet_speed': '500/50 Mbps',
                'manufacturer': 'SonicWall',
                'model': 'TZ570',
                'ip_address': '10.50.0.1',
                'mac_address': '00:17:C5:AA:BB:CC',
                'serial_number': 'SW-TZ570-001',
                'firmware_version': '7.0.1',
                'notes': 'Main firewall with content filtering and IPS',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'name': 'Office Switch',
                'device_type': 'switch',
                'manufacturer': 'Netgear',
                'model': 'GS724T',
                'ip_address': '10.50.0.2',
                'mac_address': '00:1B:2F:AA:BB:CC',
                'serial_number': 'NGS724-001',
                'firmware_version': '6.0.3.9',
                'notes': '24-port managed switch for office area',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'name': 'Production Floor Switch',
                'device_type': 'switch',
                'manufacturer': 'Netgear',
                'model': 'GS748T',
                'ip_address': '10.50.0.3',
                'mac_address': '00:1B:2F:AA:BB:DD',
                'serial_number': 'NGS748-001',
                'firmware_version': '6.0.3.9',
                'notes': '48-port switch for production floor equipment',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'name': 'Office WiFi AP-1',
                'device_type': 'wifi',
                'manufacturer': 'TP-Link',
                'model': 'EAP660 HD',
                'ip_address': '10.50.0.20',
                'mac_address': '00:1D:0F:AA:BB:01',
                'serial_number': 'TPLINK-AP-001',
                'firmware_version': '1.0.8',
                'notes': 'WiFi access point for office area',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'name': 'Warehouse WiFi AP-2',
                'device_type': 'wifi',
                'manufacturer': 'TP-Link',
                'model': 'EAP660 HD',
                'ip_address': '10.50.0.21',
                'mac_address': '00:1D:0F:AA:BB:02',
                'serial_number': 'TPLINK-AP-002',
                'firmware_version': '1.0.8',
                'notes': 'WiFi access point for warehouse area',
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
            # Acme Manufacturing endpoints (25 employees with mix of desktops and laptops)
            {
                'org_index': 4,
                'location_index': 6,
                'contact_index': 7,  # CEO
                'name': 'LAPTOP-JRICHARDSON',
                'device_type': 'laptop',
                'manufacturer': 'Dell',
                'model': 'Latitude 7430',
                'cpu': 'Intel Core i7-1265U @ 1.80GHz',
                'ram': '16GB DDR4',
                'storage': '512GB NVMe SSD',
                'operating_system': 'Windows 11 Pro',
                'software_installed': 'Microsoft Office 365, Chrome, Teams, Adobe Acrobat',
                'ip_address': '10.50.0.100',
                'mac_address': '00:50:56:AC:01:01',
                'hostname': 'LAPTOP-JRICHARDSON',
                'serial_number': 'ACM-LT-001',
                'purchase_date': (timezone.now() - timedelta(days=200)).date(),
                'warranty_expiry': (timezone.now() + timedelta(days=895)).date(),
                'notes': 'CEO laptop',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'contact_index': 8,  # CFO
                'name': 'DESK-PCOOPER',
                'device_type': 'desktop',
                'manufacturer': 'Dell',
                'model': 'OptiPlex 5090',
                'cpu': 'Intel Core i5-11500 @ 2.70GHz',
                'ram': '16GB DDR4',
                'storage': '512GB SSD',
                'operating_system': 'Windows 11 Pro',
                'software_installed': 'Microsoft Office 365, QuickBooks, Chrome, Teams',
                'ip_address': '10.50.0.101',
                'mac_address': '00:50:56:AC:01:02',
                'hostname': 'DESK-PCOOPER',
                'serial_number': 'ACM-DT-001',
                'purchase_date': (timezone.now() - timedelta(days=180)).date(),
                'warranty_expiry': (timezone.now() + timedelta(days=915)).date(),
                'notes': 'CFO desktop with dual monitors',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'contact_index': 9,  # IT Manager
                'name': 'LAPTOP-TBENNETT',
                'device_type': 'laptop',
                'manufacturer': 'Lenovo',
                'model': 'ThinkPad P15v Gen 3',
                'cpu': 'Intel Core i7-12700H @ 2.30GHz',
                'ram': '32GB DDR5',
                'storage': '1TB NVMe SSD',
                'operating_system': 'Windows 11 Pro',
                'software_installed': 'Microsoft Office 365, VMware Workstation, PuTTY, WinSCP, Wireshark, Visual Studio Code',
                'ip_address': '10.50.0.102',
                'mac_address': '00:50:56:AC:01:03',
                'hostname': 'LAPTOP-TBENNETT',
                'serial_number': 'ACM-LT-002',
                'purchase_date': (timezone.now() - timedelta(days=120)).date(),
                'warranty_expiry': (timezone.now() + timedelta(days=975)).date(),
                'notes': 'IT Manager laptop with admin tools',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'contact_index': 10,  # Office Manager
                'name': 'DESK-LMORGAN',
                'device_type': 'desktop',
                'manufacturer': 'HP',
                'model': 'ProDesk 400 G9',
                'cpu': 'Intel Core i5-12500 @ 3.00GHz',
                'ram': '16GB DDR4',
                'storage': '512GB SSD',
                'operating_system': 'Windows 11 Pro',
                'software_installed': 'Microsoft Office 365, ADP Payroll, Chrome, Teams',
                'ip_address': '10.50.0.103',
                'mac_address': '00:50:56:AC:01:04',
                'hostname': 'DESK-LMORGAN',
                'serial_number': 'ACM-DT-002',
                'purchase_date': (timezone.now() - timedelta(days=250)).date(),
                'warranty_expiry': (timezone.now() + timedelta(days=845)).date(),
                'notes': 'Office Manager desktop',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'contact_index': 11,  # Sales Manager
                'name': 'LAPTOP-RPOWELL',
                'device_type': 'laptop',
                'manufacturer': 'Dell',
                'model': 'Latitude 5430',
                'cpu': 'Intel Core i5-1235U @ 1.30GHz',
                'ram': '16GB DDR4',
                'storage': '512GB SSD',
                'operating_system': 'Windows 11 Pro',
                'software_installed': 'Microsoft Office 365, Salesforce, Chrome, Teams, Zoom',
                'ip_address': '10.50.0.104',
                'mac_address': '00:50:56:AC:01:05',
                'hostname': 'LAPTOP-RPOWELL',
                'serial_number': 'ACM-LT-003',
                'purchase_date': (timezone.now() - timedelta(days=150)).date(),
                'warranty_expiry': (timezone.now() + timedelta(days=945)).date(),
                'notes': 'Sales Manager laptop for travel',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'contact_index': 15,  # Marketing Coordinator
                'name': 'DESK-AROSS',
                'device_type': 'desktop',
                'manufacturer': 'Dell',
                'model': 'OptiPlex 7090',
                'cpu': 'Intel Core i7-11700 @ 2.50GHz',
                'ram': '32GB DDR4',
                'storage': '1TB SSD',
                'operating_system': 'Windows 11 Pro',
                'software_installed': 'Microsoft Office 365, Adobe Creative Cloud, Chrome, Canva',
                'ip_address': '10.50.0.105',
                'mac_address': '00:50:56:AC:01:06',
                'hostname': 'DESK-AROSS',
                'serial_number': 'ACM-DT-003',
                'purchase_date': (timezone.now() - timedelta(days=100)).date(),
                'warranty_expiry': (timezone.now() + timedelta(days=995)).date(),
                'notes': 'Marketing desktop with design software',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'contact_index': 22,  # Design Engineer
                'name': 'WORK-LWARD',
                'device_type': 'workstation',
                'manufacturer': 'HP',
                'model': 'Z2 G9 Tower',
                'cpu': 'Intel Xeon W-1370 @ 2.90GHz',
                'ram': '64GB DDR4 ECC',
                'storage': '2TB NVMe SSD',
                'gpu': 'NVIDIA RTX A4000',
                'operating_system': 'Windows 11 Pro for Workstations',
                'software_installed': 'AutoCAD, SolidWorks, Adobe Acrobat, Office 365',
                'ip_address': '10.50.0.106',
                'mac_address': '00:50:56:AC:01:07',
                'hostname': 'WORK-LWARD',
                'serial_number': 'ACM-WS-001',
                'purchase_date': (timezone.now() - timedelta(days=80)).date(),
                'warranty_expiry': (timezone.now() + timedelta(days=1015)).date(),
                'notes': 'CAD workstation for product design',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'contact_index': 14,  # Accountant
                'name': 'DESK-BPRICE',
                'device_type': 'desktop',
                'manufacturer': 'HP',
                'model': 'ProDesk 400 G9',
                'cpu': 'Intel Core i5-12500 @ 3.00GHz',
                'ram': '16GB DDR4',
                'storage': '512GB SSD',
                'operating_system': 'Windows 11 Pro',
                'software_installed': 'Microsoft Office 365, QuickBooks, Chrome',
                'ip_address': '10.50.0.107',
                'mac_address': '00:50:56:AC:01:08',
                'hostname': 'DESK-BPRICE',
                'serial_number': 'ACM-DT-004',
                'purchase_date': (timezone.now() - timedelta(days=220)).date(),
                'warranty_expiry': (timezone.now() + timedelta(days=875)).date(),
                'notes': 'Accounting desktop',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'contact_index': 17,  # HR Coordinator
                'name': 'DESK-HCOLEMAN',
                'device_type': 'desktop',
                'manufacturer': 'Dell',
                'model': 'OptiPlex 5090',
                'cpu': 'Intel Core i5-11500 @ 2.70GHz',
                'ram': '16GB DDR4',
                'storage': '512GB SSD',
                'operating_system': 'Windows 11 Pro',
                'software_installed': 'Microsoft Office 365, ADP Workforce, Chrome',
                'ip_address': '10.50.0.108',
                'mac_address': '00:50:56:AC:01:09',
                'hostname': 'DESK-HCOLEMAN',
                'serial_number': 'ACM-DT-005',
                'purchase_date': (timezone.now() - timedelta(days=190)).date(),
                'warranty_expiry': (timezone.now() + timedelta(days=905)).date(),
                'notes': 'HR desktop',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'contact_index': 19,  # Customer Service
                'name': 'DESK-SJENKINS',
                'device_type': 'desktop',
                'manufacturer': 'HP',
                'model': 'ProDesk 400 G9',
                'cpu': 'Intel Core i5-12500 @ 3.00GHz',
                'ram': '8GB DDR4',
                'storage': '256GB SSD',
                'operating_system': 'Windows 11 Pro',
                'software_installed': 'Microsoft Office 365, Chrome, Salesforce',
                'ip_address': '10.50.0.109',
                'mac_address': '00:50:56:AC:01:10',
                'hostname': 'DESK-SJENKINS',
                'serial_number': 'ACM-DT-006',
                'purchase_date': (timezone.now() - timedelta(days=300)).date(),
                'warranty_expiry': (timezone.now() + timedelta(days=795)).date(),
                'notes': 'Customer service desktop',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'contact_index': 25,  # Receptionist
                'name': 'DESK-CPATTERSON',
                'device_type': 'desktop',
                'manufacturer': 'HP',
                'model': 'ProDesk 400 G9',
                'cpu': 'Intel Core i3-12100 @ 3.30GHz',
                'ram': '8GB DDR4',
                'storage': '256GB SSD',
                'operating_system': 'Windows 11 Pro',
                'software_installed': 'Microsoft Office 365, Chrome',
                'ip_address': '10.50.0.110',
                'mac_address': '00:50:56:AC:01:11',
                'hostname': 'DESK-CPATTERSON',
                'serial_number': 'ACM-DT-007',
                'purchase_date': (timezone.now() - timedelta(days=350)).date(),
                'warranty_expiry': (timezone.now() + timedelta(days=745)).date(),
                'notes': 'Reception desk computer',
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
            # TechGuard MSP servers
            {
                'org_index': 3,
                'location_index': 4,
                'name': 'MSP-RMM-01',
                'server_type': 'virtual',
                'role': 'RMM Platform Server',
                'manufacturer': 'VMware',
                'model': 'Virtual Machine',
                'cpu': '8 vCPUs',
                'ram': '32GB',
                'storage': '1TB vDisk',
                'operating_system': 'Windows Server 2022',
                'software_installed': 'Datto RMM, SQL Server 2022, IIS',
                'ip_address': '192.168.100.50',
                'mac_address': '00:50:56:MSP:01:01',
                'hostname': 'msp-rmm-01',
                'serial_number': 'VMware-MSP-RMM-01',
                'notes': 'Remote monitoring and management platform',
            },
            {
                'org_index': 3,
                'location_index': 4,
                'name': 'MSP-PSA-01',
                'server_type': 'virtual',
                'role': 'PSA Ticketing System',
                'manufacturer': 'VMware',
                'model': 'Virtual Machine',
                'cpu': '4 vCPUs',
                'ram': '16GB',
                'storage': '500GB vDisk',
                'operating_system': 'Ubuntu Server 22.04 LTS',
                'software_installed': 'ConnectWise Manage, PostgreSQL 15, Nginx',
                'ip_address': '192.168.100.51',
                'mac_address': '00:50:56:MSP:01:02',
                'hostname': 'msp-psa-01',
                'serial_number': 'VMware-MSP-PSA-01',
                'notes': 'Professional services automation and ticketing',
            },
            {
                'org_index': 3,
                'location_index': 4,
                'name': 'MSP-BACKUP-01',
                'server_type': 'physical',
                'role': 'Backup Server',
                'manufacturer': 'Dell',
                'model': 'PowerEdge R740',
                'cpu': '2x Intel Xeon Silver 4214R @ 2.40GHz',
                'ram': '128GB DDR4 ECC',
                'storage': '48TB (12x 4TB HDD RAID 6)',
                'operating_system': 'Windows Server 2022',
                'software_installed': 'Veeam Backup & Replication, Datto SIRIS',
                'ip_address': '192.168.100.52',
                'mac_address': '00:1A:2B:MSP:01:03',
                'hostname': 'msp-backup-01',
                'serial_number': 'DELL-MSP-BCK-01',
                'notes': 'Centralized backup server for all MSP clients',
            },
            # Acme Manufacturing servers
            {
                'org_index': 4,
                'location_index': 6,
                'name': 'ACME-DC-01',
                'server_type': 'physical',
                'role': 'Domain Controller',
                'manufacturer': 'Dell',
                'model': 'PowerEdge T340',
                'cpu': 'Intel Xeon E-2234 @ 3.60GHz',
                'ram': '32GB DDR4 ECC',
                'storage': '2x 1TB SSD RAID 1',
                'operating_system': 'Windows Server 2022',
                'software_installed': 'Active Directory, DNS, DHCP',
                'ip_address': '10.50.0.10',
                'mac_address': '00:1A:2B:AC:01:01',
                'hostname': 'acme-dc-01.acmemfg.local',
                'serial_number': 'ACME-DC-001',
                'notes': 'Primary domain controller and DNS server',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'name': 'ACME-FILE-01',
                'server_type': 'physical',
                'role': 'File Server',
                'manufacturer': 'HPE',
                'model': 'ProLiant ML110 Gen10',
                'cpu': 'Intel Xeon Silver 4210R @ 2.40GHz',
                'ram': '64GB DDR4 ECC',
                'storage': '24TB (6x 4TB HDD RAID 10)',
                'operating_system': 'Windows Server 2022',
                'software_installed': 'File Services, DFS, Shadow Copies',
                'ip_address': '10.50.0.11',
                'mac_address': '00:1A:2B:AC:01:02',
                'hostname': 'acme-file-01.acmemfg.local',
                'serial_number': 'ACME-FILE-001',
                'notes': 'File server with department shares',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'name': 'ACME-SQL-01',
                'server_type': 'physical',
                'role': 'Database Server',
                'manufacturer': 'Dell',
                'model': 'PowerEdge R440',
                'cpu': '2x Intel Xeon Silver 4214 @ 2.20GHz',
                'ram': '128GB DDR4 ECC',
                'storage': '4TB (4x 1TB SSD RAID 10)',
                'operating_system': 'Windows Server 2022',
                'software_installed': 'SQL Server 2022 Standard, SSMS',
                'ip_address': '10.50.0.12',
                'mac_address': '00:1A:2B:AC:01:03',
                'hostname': 'acme-sql-01.acmemfg.local',
                'serial_number': 'ACME-SQL-001',
                'notes': 'SQL Server for ERP and accounting systems',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'name': 'ACME-APP-01',
                'server_type': 'virtual',
                'role': 'Application Server',
                'manufacturer': 'Hyper-V',
                'model': 'Virtual Machine',
                'cpu': '4 vCPUs',
                'ram': '16GB',
                'storage': '500GB vDisk',
                'operating_system': 'Windows Server 2022',
                'software_installed': 'IIS, .NET Framework 4.8, QuickBooks Enterprise',
                'ip_address': '10.50.0.13',
                'mac_address': '00:15:5D:AC:01:04',
                'hostname': 'acme-app-01.acmemfg.local',
                'serial_number': 'HyperV-ACME-APP-01',
                'notes': 'Application server for QuickBooks and internal apps',
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
            # TechGuard MSP peripherals
            {
                'org_index': 3,
                'location_index': 4,
                'name': 'MSP Office Printer',
                'device_type': 'multifunction',
                'manufacturer': 'Brother',
                'model': 'MFC-L6900DW',
                'ip_address': '192.168.100.200',
                'mac_address': '00:1B:A9:MSP:01:01',
                'serial_number': 'MSP-PRT-001',
                'notes': 'Office multifunction printer',
            },
            {
                'org_index': 3,
                'location_index': 4,
                'name': 'MSP Server Room UPS',
                'device_type': 'ups',
                'manufacturer': 'APC',
                'model': 'Smart-UPS 2200VA',
                'ip_address': '192.168.100.210',
                'mac_address': '00:C0:B7:MSP:01:01',
                'serial_number': 'MSP-UPS-001',
                'notes': 'UPS for server room equipment',
            },
            {
                'org_index': 3,
                'location_index': 4,
                'name': 'MSP Backup NAS',
                'device_type': 'nas',
                'manufacturer': 'Synology',
                'model': 'DS1821+',
                'ip_address': '192.168.100.220',
                'mac_address': '00:11:32:MSP:01:01',
                'serial_number': 'MSP-NAS-001',
                'notes': 'NAS for local backup storage - 64TB capacity',
            },
            # Acme Manufacturing peripherals
            {
                'org_index': 4,
                'location_index': 6,
                'name': 'Office Copier',
                'device_type': 'multifunction',
                'manufacturer': 'Xerox',
                'model': 'VersaLink C7025',
                'ip_address': '10.50.0.200',
                'mac_address': '00:00:AA:AC:01:01',
                'serial_number': 'ACME-COPIER-001',
                'notes': 'Main office multifunction copier/printer',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'name': 'Warehouse Printer',
                'device_type': 'printer',
                'manufacturer': 'Zebra',
                'model': 'ZT230',
                'ip_address': '10.50.0.201',
                'mac_address': '00:07:4D:AC:01:02',
                'serial_number': 'ACME-ZEBRA-001',
                'notes': 'Label printer for shipping department',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'name': 'Server Room UPS',
                'device_type': 'ups',
                'manufacturer': 'APC',
                'model': 'Smart-UPS 1500VA',
                'ip_address': '10.50.0.210',
                'mac_address': '00:C0:B7:AC:01:01',
                'serial_number': 'ACME-UPS-001',
                'notes': 'UPS for server room - 1 hour runtime',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'name': 'Backup NAS',
                'device_type': 'nas',
                'manufacturer': 'QNAP',
                'model': 'TS-453D',
                'ip_address': '10.50.0.220',
                'mac_address': '00:08:9B:AC:01:01',
                'serial_number': 'ACME-NAS-001',
                'notes': 'Network storage for backups - 16TB (4x4TB RAID 5)',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'name': 'Reception Scanner',
                'device_type': 'scanner',
                'manufacturer': 'Canon',
                'model': 'imageFORMULA DR-C225',
                'ip_address': '10.50.0.230',
                'mac_address': '00:1E:8F:AC:01:02',
                'serial_number': 'ACME-SCAN-001',
                'notes': 'Document scanner at reception desk',
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

    def create_software(self, organizations, contacts, users):
        """Create software licenses and applications."""
        software_list = []

        # Calculate dates for licenses
        today = timezone.now().date()

        software_data = [
            # Tech Solutions Inc software
            {
                'org_index': 0,
                'contact_index': 0,  # Michael Anderson
                'name': 'Microsoft 365 Business Premium',
                'software_type': 'microsoft365',
                'license_key': 'XXXXX-XXXXX-XXXXX-XXXXX-XXXXX',
                'version': 'Business Premium',
                'license_type': 'subscription',
                'purchase_date': today - timedelta(days=365),
                'expiry_date': today + timedelta(days=365),
                'vendor': 'Microsoft',
                'cost': 22.00,
                'quantity': 50,
                'notes': 'Company-wide Microsoft 365 subscription including Office apps, Exchange, Teams, and OneDrive',
            },
            {
                'org_index': 0,
                'contact_index': 0,  # Michael Anderson
                'name': 'Sophos Intercept X',
                'software_type': 'endpoint_protection',
                'license_key': 'SOPHOS-XXXX-XXXX-XXXX',
                'version': 'Advanced',
                'license_type': 'subscription',
                'purchase_date': today - timedelta(days=180),
                'expiry_date': today + timedelta(days=545),
                'vendor': 'Sophos',
                'cost': 45.00,
                'quantity': 50,
                'notes': 'Endpoint protection with EDR capabilities for all workstations',
            },
            {
                'org_index': 0,
                'contact_index': 1,  # Sarah Williams
                'name': 'Adobe Creative Cloud',
                'software_type': 'design',
                'license_key': 'ADOBE-XXXX-XXXX-XXXX',
                'version': 'All Apps',
                'license_type': 'subscription',
                'purchase_date': today - timedelta(days=200),
                'expiry_date': today + timedelta(days=165),
                'vendor': 'Adobe',
                'cost': 54.99,
                'quantity': 5,
                'notes': 'Creative Cloud subscription for design team - Photoshop, Illustrator, InDesign, Premiere Pro',
            },
            {
                'org_index': 0,
                'contact_index': 1,  # Sarah Williams
                'name': 'Visual Studio Professional',
                'software_type': 'development',
                'license_key': 'VS-PROF-XXXX-XXXX',
                'version': '2024',
                'license_type': 'subscription',
                'purchase_date': today - timedelta(days=90),
                'expiry_date': today + timedelta(days=275),
                'vendor': 'Microsoft',
                'cost': 45.00,
                'quantity': 10,
                'notes': 'Development IDE for software development team',
            },
            # Digital Innovations Ltd software
            {
                'org_index': 1,
                'contact_index': 2,  # David Brown
                'name': 'Microsoft 365 E3',
                'software_type': 'microsoft365',
                'license_key': 'M365-E3-XXXX-XXXX',
                'version': 'E3',
                'license_type': 'subscription',
                'purchase_date': today - timedelta(days=400),
                'expiry_date': today + timedelta(days=330),
                'vendor': 'Microsoft',
                'cost': 36.00,
                'quantity': 75,
                'notes': 'Enterprise E3 licenses for enhanced security and compliance features',
            },
            {
                'org_index': 1,
                'contact_index': 2,  # David Brown
                'name': 'CrowdStrike Falcon',
                'software_type': 'endpoint_protection',
                'license_key': 'CROWD-XXXX-XXXX-XXXX',
                'version': 'Enterprise',
                'license_type': 'subscription',
                'purchase_date': today - timedelta(days=150),
                'expiry_date': today + timedelta(days=215),
                'vendor': 'CrowdStrike',
                'cost': 99.00,
                'quantity': 75,
                'notes': 'Advanced threat protection and EDR solution',
            },
            {
                'org_index': 1,
                'contact_index': 2,  # David Brown
                'name': 'Slack Business+',
                'software_type': 'subscription',
                'license_key': 'SLACK-XXXX-XXXX-XXXX',
                'version': 'Business+',
                'license_type': 'subscription',
                'purchase_date': today - timedelta(days=300),
                'expiry_date': today + timedelta(days=65),
                'vendor': 'Salesforce',
                'cost': 12.50,
                'quantity': 75,
                'notes': 'Team communication and collaboration platform',
            },
            # Cloud Systems Corp software
            {
                'org_index': 2,
                'contact_index': 3,  # Emily Davis
                'name': 'Microsoft 365 E5',
                'software_type': 'microsoft365',
                'license_key': 'M365-E5-XXXX-XXXX',
                'version': 'E5',
                'license_type': 'subscription',
                'purchase_date': today - timedelta(days=500),
                'expiry_date': today + timedelta(days=230),
                'vendor': 'Microsoft',
                'cost': 57.00,
                'quantity': 100,
                'notes': 'Premium E5 licenses with advanced security, compliance, and analytics',
            },
            {
                'org_index': 2,
                'contact_index': 3,  # Emily Davis
                'name': 'Veeam Backup & Replication',
                'software_type': 'other',
                'license_key': 'VEEAM-XXXX-XXXX-XXXX',
                'version': 'Enterprise Plus',
                'license_type': 'subscription',
                'purchase_date': today - timedelta(days=250),
                'expiry_date': today + timedelta(days=115),
                'vendor': 'Veeam',
                'cost': 950.00,
                'quantity': 100,
                'notes': 'Backup solution for virtual and physical servers',
            },
            {
                'org_index': 2,
                'contact_index': 3,  # Emily Davis
                'name': 'VMware vSphere',
                'software_type': 'other',
                'license_key': 'VMWARE-XXXX-XXXX-XXXX',
                'version': 'Enterprise Plus',
                'license_type': 'subscription',
                'purchase_date': today - timedelta(days=600),
                'expiry_date': today + timedelta(days=130),
                'vendor': 'VMware',
                'cost': 3595.00,
                'quantity': 10,
                'notes': 'Virtualization platform for datacenter infrastructure',
            },
            # TechGuard MSP software
            {
                'org_index': 3,
                'contact_index': 4,  # Robert Miller
                'name': 'Microsoft 365 Business Standard',
                'software_type': 'microsoft365',
                'license_key': 'M365-BS-XXXX-XXXX',
                'version': 'Business Standard',
                'license_type': 'subscription',
                'purchase_date': today - timedelta(days=200),
                'expiry_date': today + timedelta(days=165),
                'vendor': 'Microsoft',
                'cost': 12.50,
                'quantity': 15,
                'notes': 'Internal use for MSP staff - Office apps, Exchange, Teams',
            },
            {
                'org_index': 3,
                'contact_index': 4,  # Robert Miller
                'name': 'Datto RMM',
                'software_type': 'other',
                'license_key': 'DATTO-RMM-XXXX-XXXX',
                'version': 'Professional',
                'license_type': 'subscription',
                'purchase_date': today - timedelta(days=400),
                'expiry_date': today + timedelta(days=330),
                'vendor': 'Datto',
                'cost': 2500.00,
                'quantity': 1,
                'notes': 'Remote monitoring and management platform for client endpoints',
            },
            {
                'org_index': 3,
                'contact_index': 5,  # Jennifer Taylor
                'name': 'ConnectWise Manage',
                'software_type': 'other',
                'license_key': 'CW-MANAGE-XXXX-XXXX',
                'version': 'Cloud',
                'license_type': 'subscription',
                'purchase_date': today - timedelta(days=450),
                'expiry_date': today + timedelta(days=280),
                'vendor': 'ConnectWise',
                'cost': 99.00,
                'quantity': 10,
                'notes': 'PSA (Professional Services Automation) for ticketing and project management',
            },
            {
                'org_index': 3,
                'contact_index': 5,  # Jennifer Taylor
                'name': 'SentinelOne Singularity',
                'software_type': 'endpoint_protection',
                'license_key': 'S1-XXXX-XXXX-XXXX',
                'version': 'Complete',
                'license_type': 'subscription',
                'purchase_date': today - timedelta(days=180),
                'expiry_date': today + timedelta(days=185),
                'vendor': 'SentinelOne',
                'cost': 65.00,
                'quantity': 500,
                'notes': 'AI-powered endpoint protection deployed to all client workstations',
            },
            # Acme Manufacturing software
            {
                'org_index': 4,
                'contact_index': 9,  # Thomas Bennett (IT Manager)
                'name': 'Microsoft 365 Business Basic',
                'software_type': 'microsoft365',
                'license_key': 'M365-BB-XXXX-XXXX',
                'version': 'Business Basic',
                'license_type': 'subscription',
                'purchase_date': today - timedelta(days=100),
                'expiry_date': today + timedelta(days=265),
                'vendor': 'Microsoft',
                'cost': 6.00,
                'quantity': 25,
                'notes': 'Basic Office 365 licenses for all staff - email, Teams, OneDrive',
            },
            {
                'org_index': 4,
                'contact_index': 9,  # Thomas Bennett
                'name': 'ESET Endpoint Security',
                'software_type': 'endpoint_protection',
                'license_key': 'ESET-XXXX-XXXX-XXXX',
                'version': 'Standard',
                'license_type': 'subscription',
                'purchase_date': today - timedelta(days=220),
                'expiry_date': today + timedelta(days=145),
                'vendor': 'ESET',
                'cost': 39.00,
                'quantity': 30,
                'notes': 'Antivirus and endpoint protection for all computers',
            },
            {
                'org_index': 4,
                'contact_index': 9,  # Thomas Bennett
                'name': 'QuickBooks Desktop Enterprise',
                'software_type': 'other',
                'license_key': 'QB-ENT-XXXX-XXXX',
                'version': '2024',
                'license_type': 'subscription',
                'purchase_date': today - timedelta(days=300),
                'expiry_date': today + timedelta(days=65),
                'vendor': 'Intuit',
                'cost': 1750.00,
                'quantity': 5,
                'notes': 'Accounting software for finance department',
            },
            {
                'org_index': 4,
                'contact_index': 9,  # Thomas Bennett
                'name': 'AutoCAD',
                'software_type': 'design',
                'license_key': 'ACAD-XXXX-XXXX-XXXX',
                'version': '2024',
                'license_type': 'subscription',
                'purchase_date': today - timedelta(days=400),
                'expiry_date': today + timedelta(days=330),
                'vendor': 'Autodesk',
                'cost': 220.00,
                'quantity': 3,
                'notes': 'CAD software for engineering and design team',
            },
            {
                'org_index': 4,
                'contact_index': 9,  # Thomas Bennett
                'name': 'Acronis Cyber Protect',
                'software_type': 'other',
                'license_key': 'ACRONIS-XXXX-XXXX',
                'version': 'Standard',
                'license_type': 'subscription',
                'purchase_date': today - timedelta(days=150),
                'expiry_date': today + timedelta(days=215),
                'vendor': 'Acronis',
                'cost': 599.00,
                'quantity': 1,
                'notes': 'Backup solution for servers and workstations',
            },
        ]

        for software_data_item in software_data:
            org_index = software_data_item.pop('org_index')
            contact_index = software_data_item.pop('contact_index', None)

            software = Software.objects.create(
                organization=organizations[org_index],
                assigned_to=contacts[contact_index] if contact_index is not None else None,
                created_by=random.choice(users),
                **software_data_item
            )
            software_list.append(software)

        return software_list

    def create_backups(self, organizations, locations, servers, users):
        """Create backup solutions and configurations."""
        backups = []

        # Calculate dates for backup tracking
        now = timezone.now()
        today = now.date()

        backup_data = [
            # Tech Solutions Inc backups
            {
                'org_index': 0,
                'location_index': 0,
                'name': 'Server Room Backup - Local NAS',
                'backup_type': 'server',
                'vendor': 'Synology Active Backup',
                'frequency': 'Daily at 2 AM',
                'retention_period': '30 days local',
                'storage_location': 'On-premise NAS - Synology DS920+',
                'storage_capacity': '12TB',
                'target_systems': 'Windows Servers, File Servers, Domain Controllers',
                'last_backup_date': now - timedelta(hours=8),
                'next_backup_date': now + timedelta(hours=16),
                'backup_status': 'active',
                'cost': 0.00,
                'cost_period': 'one_time',
                'notes': 'Local backup to Synology NAS using Active Backup for Business. Hardware already purchased.',
            },
            {
                'org_index': 0,
                'location_index': 0,
                'name': 'Veeam Cloud Connect',
                'backup_type': 'server',
                'vendor': 'Veeam',
                'frequency': 'Daily incremental, Weekly full',
                'retention_period': '90 days cloud',
                'storage_location': 'Veeam Cloud Connect - AWS S3',
                'storage_capacity': '5TB',
                'target_systems': 'Critical VMs, SQL Databases, Exchange Server',
                'last_backup_date': now - timedelta(hours=12),
                'next_backup_date': now + timedelta(hours=12),
                'backup_status': 'active',
                'cost': 450.00,
                'cost_period': 'monthly',
                'notes': 'Offsite cloud backup replication for disaster recovery',
            },
            {
                'org_index': 0,
                'location_index': 0,
                'name': 'Microsoft 365 Backup - AvePoint',
                'backup_type': 'microsoft365',
                'vendor': 'AvePoint Cloud Backup',
                'frequency': 'Every 12 hours',
                'retention_period': 'Unlimited',
                'storage_location': 'AvePoint Cloud Storage',
                'storage_capacity': '500GB',
                'target_systems': 'Exchange Online, SharePoint, OneDrive, Teams',
                'last_backup_date': now - timedelta(hours=6),
                'next_backup_date': now + timedelta(hours=6),
                'backup_status': 'active',
                'cost': 3.00,
                'cost_period': 'monthly',
                'notes': 'Microsoft 365 backup for 50 users - $3/user/month',
            },
            {
                'org_index': 0,
                'location_index': 1,
                'name': 'Branch Office Endpoint Backup',
                'backup_type': 'endpoint',
                'vendor': 'Acronis Cyber Backup',
                'frequency': 'Daily',
                'retention_period': '30 days',
                'storage_location': 'Acronis Cloud',
                'storage_capacity': '500GB',
                'target_systems': 'Branch laptops and workstations',
                'last_backup_date': now - timedelta(hours=10),
                'next_backup_date': now + timedelta(hours=14),
                'backup_status': 'active',
                'cost': 199.00,
                'cost_period': 'monthly',
                'notes': 'Cloud backup for 10 endpoint devices at branch office',
            },
            # Digital Innovations Ltd backups
            {
                'org_index': 1,
                'location_index': 2,
                'name': 'Enterprise Server Backup',
                'backup_type': 'server',
                'vendor': 'Commvault',
                'frequency': 'Continuous data protection',
                'retention_period': '1 year',
                'storage_location': 'On-premise data domain + AWS S3 Glacier',
                'storage_capacity': '50TB',
                'target_systems': 'All production servers, databases, file servers, applications',
                'last_backup_date': now - timedelta(minutes=30),
                'next_backup_date': now + timedelta(minutes=30),
                'backup_status': 'active',
                'cost': 2500.00,
                'cost_period': 'monthly',
                'notes': 'Enterprise-grade backup solution with continuous protection and long-term retention',
            },
            {
                'org_index': 1,
                'location_index': 2,
                'name': 'Microsoft 365 Backup - Veeam',
                'backup_type': 'microsoft365',
                'vendor': 'Veeam Backup for Microsoft 365',
                'frequency': 'Every 6 hours',
                'retention_period': '7 years',
                'storage_location': 'Azure Blob Storage',
                'storage_capacity': '2TB',
                'target_systems': 'Exchange Online, SharePoint, OneDrive for Business, Teams',
                'last_backup_date': now - timedelta(hours=3),
                'next_backup_date': now + timedelta(hours=3),
                'backup_status': 'active',
                'cost': 5.00,
                'cost_period': 'monthly',
                'notes': 'M365 backup for 75 users with extended retention for compliance',
            },
            {
                'org_index': 1,
                'location_index': 2,
                'name': 'Database Backup - SQL Server',
                'backup_type': 'database',
                'vendor': 'SQL Server Native Backup to Azure',
                'frequency': 'Full daily, Transaction log every 15 minutes',
                'retention_period': '30 days',
                'storage_location': 'Azure SQL Database Backup Storage',
                'storage_capacity': '5TB',
                'target_systems': 'Production SQL Servers, Data Warehouses',
                'last_backup_date': now - timedelta(minutes=15),
                'next_backup_date': now + timedelta(minutes=15),
                'backup_status': 'active',
                'cost': 350.00,
                'cost_period': 'monthly',
                'notes': 'Automated SQL backup with point-in-time recovery capability',
            },
            # Cloud Systems Corp backups
            {
                'org_index': 2,
                'location_index': 3,
                'name': 'Datacenter Primary Backup',
                'backup_type': 'server',
                'vendor': 'Rubrik',
                'frequency': 'Continuous',
                'retention_period': '5 years',
                'storage_location': 'Rubrik cluster + AWS S3 archive',
                'storage_capacity': '100TB',
                'target_systems': 'VMware VMs, Physical servers, NAS, Kubernetes',
                'last_backup_date': now - timedelta(minutes=10),
                'next_backup_date': now + timedelta(minutes=10),
                'backup_status': 'active',
                'cost': 8500.00,
                'cost_period': 'monthly',
                'notes': 'Enterprise data management platform with instant recovery and cloud archival',
            },
            {
                'org_index': 2,
                'location_index': 3,
                'name': 'AWS Cloud Backup',
                'backup_type': 'cloud',
                'vendor': 'AWS Backup',
                'frequency': 'Hourly incremental',
                'retention_period': '90 days',
                'storage_location': 'AWS S3 + Glacier',
                'storage_capacity': '25TB',
                'target_systems': 'EC2 instances, RDS databases, EFS file systems, DynamoDB',
                'last_backup_date': now - timedelta(minutes=45),
                'next_backup_date': now + timedelta(minutes=15),
                'backup_status': 'active',
                'cost': 1250.00,
                'cost_period': 'monthly',
                'notes': 'Centralized backup for all AWS cloud resources across multiple regions',
            },
            {
                'org_index': 2,
                'location_index': 3,
                'name': 'Microsoft 365 Enterprise Backup',
                'backup_type': 'microsoft365',
                'vendor': 'Barracuda Cloud-to-Cloud Backup',
                'frequency': 'Every 4 hours',
                'retention_period': 'Unlimited',
                'storage_location': 'Barracuda Cloud Storage',
                'storage_capacity': '5TB',
                'target_systems': 'Exchange Online, SharePoint, OneDrive, Teams, all M365 services',
                'last_backup_date': now - timedelta(hours=2),
                'next_backup_date': now + timedelta(hours=2),
                'backup_status': 'active',
                'cost': 4.00,
                'cost_period': 'monthly',
                'notes': 'Comprehensive M365 backup for 100 users with unlimited retention',
            },
            {
                'org_index': 2,
                'location_index': 3,
                'name': 'PostgreSQL Database Backup',
                'backup_type': 'database',
                'vendor': 'pgBackRest',
                'frequency': 'Full daily, Incremental every hour',
                'retention_period': '60 days',
                'storage_location': 'Dedicated backup server + S3',
                'storage_capacity': '10TB',
                'target_systems': 'PostgreSQL production and staging databases',
                'last_backup_date': now - timedelta(hours=1),
                'next_backup_date': now + timedelta(hours=1),
                'backup_status': 'active',
                'cost': 275.00,
                'cost_period': 'monthly',
                'notes': 'Point-in-time recovery for PostgreSQL with WAL archiving',
            },
            # TechGuard MSP backups
            {
                'org_index': 3,
                'location_index': 4,
                'name': 'MSP Internal Server Backup',
                'backup_type': 'server',
                'vendor': 'Datto SIRIS',
                'frequency': 'Every 5 minutes',
                'retention_period': '30 days local, 1 year cloud',
                'storage_location': 'Datto appliance + Datto Cloud',
                'storage_capacity': '8TB',
                'target_systems': 'Internal servers, NOC systems, management tools',
                'last_backup_date': now - timedelta(minutes=5),
                'next_backup_date': now + timedelta(minutes=5),
                'backup_status': 'active',
                'cost': 899.00,
                'cost_period': 'monthly',
                'notes': 'BCDR solution for MSP infrastructure with instant virtualization',
            },
            {
                'org_index': 3,
                'location_index': 4,
                'name': 'Client Backup Service - Package A',
                'backup_type': 'server',
                'vendor': 'Datto ALTO',
                'frequency': 'Hourly',
                'retention_period': '30 days',
                'storage_location': 'Datto Cloud',
                'storage_capacity': '50TB aggregate',
                'target_systems': 'Client servers across multiple locations',
                'last_backup_date': now - timedelta(minutes=30),
                'next_backup_date': now + timedelta(minutes=30),
                'backup_status': 'active',
                'cost': 5500.00,
                'cost_period': 'monthly',
                'notes': 'Managed backup service for 50+ client servers',
            },
            {
                'org_index': 3,
                'location_index': 4,
                'name': 'Client Microsoft 365 Backup',
                'backup_type': 'microsoft365',
                'vendor': 'Datto SaaS Protection',
                'frequency': 'Every 12 hours',
                'retention_period': '7 years',
                'storage_location': 'Datto Cloud',
                'storage_capacity': '20TB',
                'target_systems': 'M365 for all managed clients - Exchange, SharePoint, OneDrive, Teams',
                'last_backup_date': now - timedelta(hours=8),
                'next_backup_date': now + timedelta(hours=4),
                'backup_status': 'active',
                'cost': 2.50,
                'cost_period': 'monthly',
                'notes': 'M365 backup service for ~800 client users across multiple tenants',
            },
            {
                'org_index': 3,
                'location_index': 4,
                'name': 'Client Endpoint Backup',
                'backup_type': 'endpoint',
                'vendor': 'Acronis Cyber Protect',
                'frequency': 'Daily',
                'retention_period': '30 days',
                'storage_location': 'Acronis Cloud',
                'storage_capacity': '25TB',
                'target_systems': 'Client workstations and laptops',
                'last_backup_date': now - timedelta(hours=18),
                'next_backup_date': now + timedelta(hours=6),
                'backup_status': 'active',
                'cost': 7500.00,
                'cost_period': 'monthly',
                'notes': 'Endpoint backup for 500+ client machines with ransomware protection',
            },
            {
                'org_index': 3,
                'location_index': 5,
                'name': 'Remote Support Center Backup',
                'backup_type': 'nas',
                'vendor': 'Synology C2',
                'frequency': 'Daily',
                'retention_period': '90 days',
                'storage_location': 'Synology C2 Cloud',
                'storage_capacity': '2TB',
                'target_systems': 'Support center NAS file shares',
                'last_backup_date': now - timedelta(hours=20),
                'next_backup_date': now + timedelta(hours=4),
                'backup_status': 'active',
                'cost': 99.00,
                'cost_period': 'monthly',
                'notes': 'Cloud backup for remote office NAS storage',
            },
            # Acme Manufacturing backups
            {
                'org_index': 4,
                'location_index': 6,
                'name': 'Server Backup - Local & Cloud',
                'backup_type': 'server',
                'vendor': 'Veeam Backup & Replication',
                'frequency': 'Daily at 11 PM',
                'retention_period': '14 days local, 90 days cloud',
                'storage_location': 'QNAP NAS + Wasabi Cloud',
                'storage_capacity': '8TB local, 5TB cloud',
                'target_systems': 'Domain Controller, File Server, QuickBooks Server',
                'last_backup_date': now - timedelta(hours=13),
                'next_backup_date': now + timedelta(hours=11),
                'backup_status': 'active',
                'cost': 149.00,
                'cost_period': 'monthly',
                'notes': 'Hybrid backup solution - local NAS for quick restores, cloud for DR',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'name': 'Microsoft 365 Backup',
                'backup_type': 'microsoft365',
                'vendor': 'AvePoint Cloud Backup',
                'frequency': 'Daily',
                'retention_period': '1 year',
                'storage_location': 'AvePoint Cloud',
                'storage_capacity': '250GB',
                'target_systems': 'Exchange Online, OneDrive, Teams for all 25 users',
                'last_backup_date': now - timedelta(hours=15),
                'next_backup_date': now + timedelta(hours=9),
                'backup_status': 'active',
                'cost': 75.00,
                'cost_period': 'monthly',
                'notes': 'M365 backup for 25 users at $3/user/month',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'name': 'Production CAD Files Backup',
                'backup_type': 'nas',
                'vendor': 'QNAP Snapshot Replication',
                'frequency': 'Hourly snapshots, Daily replication',
                'retention_period': '30 days snapshots, 180 days replication',
                'storage_location': 'Primary NAS + Secondary NAS offsite',
                'storage_capacity': '4TB',
                'target_systems': 'AutoCAD files, Engineering documents, Production drawings',
                'last_backup_date': now - timedelta(hours=1),
                'next_backup_date': now + timedelta(hours=1),
                'backup_status': 'active',
                'cost': 0.00,
                'cost_period': 'one_time',
                'notes': 'Critical engineering files backed up with snapshot technology. Hardware cost already paid.',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'name': 'QuickBooks Database Backup',
                'backup_type': 'database',
                'vendor': 'Intuit QuickBooks Auto Backup',
                'frequency': 'Every 4 hours during business hours',
                'retention_period': '60 days',
                'storage_location': 'Local server + Intuit cloud',
                'storage_capacity': '100GB',
                'target_systems': 'QuickBooks company files and databases',
                'last_backup_date': now - timedelta(hours=3),
                'next_backup_date': now + timedelta(hours=1),
                'backup_status': 'active',
                'cost': 0.00,
                'cost_period': 'one_time',
                'notes': 'Automated backup included with QuickBooks Enterprise subscription',
            },
            {
                'org_index': 4,
                'location_index': 6,
                'name': 'Critical Workstation Backup',
                'backup_type': 'endpoint',
                'vendor': 'Acronis Cyber Protect',
                'frequency': 'Daily',
                'retention_period': '30 days',
                'storage_location': 'Acronis Cloud',
                'storage_capacity': '500GB',
                'target_systems': 'CEO, CFO, IT Manager, and Engineering workstations',
                'last_backup_date': now - timedelta(hours=20),
                'next_backup_date': now + timedelta(hours=4),
                'backup_status': 'active',
                'cost': 199.00,
                'cost_period': 'monthly',
                'notes': 'Cloud backup for 5 critical user workstations with important local data',
            },
        ]

        for backup_data_item in backup_data:
            org_index = backup_data_item.pop('org_index')
            location_index = backup_data_item.pop('location_index', None)

            backup = Backup.objects.create(
                organization=organizations[org_index],
                location=locations[location_index] if location_index is not None else None,
                created_by=random.choice(users),
                **backup_data_item
            )
            backups.append(backup)

        return backups
