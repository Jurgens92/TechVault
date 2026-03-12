"""
Tests for core CRUD API endpoints.

Tests cover:
- Organization CRUD (create, read, update, delete)
- Location CRUD with organization filtering
- Contact CRUD with CSV import
- Documentation CRUD
- Configuration CRUD
- Network Device CRUD
- Server, EndpointUser, Peripheral CRUD
- Software and VoIP CRUD with assignments
- Backup CRUD
- Organization search
- Authentication requirements
"""
import pyotp
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from users.auth_views import hash_backup_code

from core.models import (
    Organization, Location, Contact, Documentation,
    PasswordEntry, Configuration, NetworkDevice, EndpointUser,
    Server, Peripheral, Software, SoftwareAssignment,
    Backup, VoIP, VoIPAssignment, OrganizationMember,
)

User = get_user_model()


class AuthenticatedTestCase(TestCase):
    """Base class that provides an authenticated user with 2FA for API tests."""

    def setUp(self):
        self.client = APIClient()
        self.password = 'SecureP@ssw0rd123'
        self.twofa_secret = pyotp.random_base32()

        self.user = User.objects.create_user(
            email='testuser@example.com',
            password=self.password,
            first_name='Test',
            last_name='User',
            is_staff=True,
        )
        self.user.twofa_enabled = True
        self.user.twofa_secret = self.twofa_secret
        self.user.twofa_backup_codes = [hash_backup_code('BACKUP01')]
        self.user.save()

        # Force authenticate to bypass 2FA middleware in tests
        self.client.force_authenticate(user=self.user)


class OrganizationCRUDTestCase(AuthenticatedTestCase):
    """Test Organization CRUD operations."""

    def test_create_organization(self):
        response = self.client.post('/api/organizations/', {
            'name': 'Acme Corp',
            'description': 'A test organization',
            'email': 'info@acme.com',
            'phone': '+1-555-0100',
            'address': '123 Main St',
            'city': 'Springfield',
            'state_province': 'IL',
            'postal_code': '62701',
            'country': 'United States',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Acme Corp')
        # Verify organization was created in DB
        self.assertTrue(Organization.objects.filter(name='Acme Corp').exists())

    def test_create_organization_creates_default_location(self):
        """Creating an org with full address should auto-create Head Office location."""
        self.client.post('/api/organizations/', {
            'name': 'Acme Corp',
            'address': '123 Main St',
            'city': 'Springfield',
            'state_province': 'IL',
            'postal_code': '62701',
            'country': 'United States',
        })
        org = Organization.objects.get(name='Acme Corp')
        self.assertTrue(Location.objects.filter(organization=org, name='Head Office').exists())

    def test_create_organization_adds_owner_membership(self):
        """Creating an org should add the creator as owner."""
        self.client.post('/api/organizations/', {
            'name': 'Acme Corp',
        })
        org = Organization.objects.get(name='Acme Corp')
        membership = OrganizationMember.objects.get(organization=org, user=self.user)
        self.assertEqual(membership.role, 'owner')

    def test_list_organizations(self):
        Organization.objects.create(name='Org A', created_by=self.user)
        Organization.objects.create(name='Org B', created_by=self.user)

        response = self.client.get('/api/organizations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_retrieve_organization(self):
        org = Organization.objects.create(name='Org A', created_by=self.user)
        response = self.client.get(f'/api/organizations/{org.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Org A')

    def test_update_organization(self):
        org = Organization.objects.create(name='Old Name', created_by=self.user)
        response = self.client.patch(f'/api/organizations/{org.id}/', {
            'name': 'New Name',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        org.refresh_from_db()
        self.assertEqual(org.name, 'New Name')

    def test_delete_organization_soft_deletes(self):
        org = Organization.objects.create(name='Delete Me', created_by=self.user)
        response = self.client.delete(f'/api/organizations/{org.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should be soft-deleted (not visible in default queryset)
        self.assertFalse(Organization.objects.filter(id=org.id).exists())
        # But should still exist in all_objects
        self.assertTrue(Organization.all_objects.filter(id=org.id).exists())

    def test_search_organizations(self):
        Organization.objects.create(name='Acme Corp', created_by=self.user)
        Organization.objects.create(name='Widget Inc', created_by=self.user)

        response = self.client.get('/api/organizations/search/', {'q': 'Acme'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Acme Corp')

    def test_organization_stats(self):
        org = Organization.objects.create(name='Stats Org', created_by=self.user)
        Location.objects.create(organization=org, name='Office', created_by=self.user)
        Contact.objects.create(
            organization=org, first_name='John', last_name='Doe',
            created_by=self.user
        )

        response = self.client.get(f'/api/organizations/{org.id}/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['locations_count'], 1)
        self.assertEqual(response.data['contacts_count'], 1)

    def test_unauthenticated_request_rejected(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/organizations/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LocationCRUDTestCase(AuthenticatedTestCase):
    """Test Location CRUD operations."""

    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(name='Test Org', created_by=self.user)

    def test_create_location(self):
        response = self.client.post('/api/locations/', {
            'organization': str(self.org.id),
            'name': 'Branch Office',
            'address': '456 Oak Ave',
            'city': 'Portland',
            'state_province': 'OR',
            'postal_code': '97201',
            'country': 'United States',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Branch Office')

    def test_list_locations(self):
        Location.objects.create(organization=self.org, name='Office A', created_by=self.user)
        Location.objects.create(organization=self.org, name='Office B', created_by=self.user)

        response = self.client.get('/api/locations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_filter_locations_by_organization(self):
        other_org = Organization.objects.create(name='Other Org', created_by=self.user)
        Location.objects.create(organization=self.org, name='Office A', created_by=self.user)
        Location.objects.create(organization=other_org, name='Office B', created_by=self.user)

        response = self.client.get('/api/locations/by_organization/', {
            'organization_id': str(self.org.id)
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Office A')

    def test_update_location(self):
        loc = Location.objects.create(
            organization=self.org, name='Old Name', created_by=self.user
        )
        response = self.client.patch(f'/api/locations/{loc.id}/', {
            'name': 'New Name'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        loc.refresh_from_db()
        self.assertEqual(loc.name, 'New Name')

    def test_delete_location(self):
        loc = Location.objects.create(
            organization=self.org, name='Delete Me', created_by=self.user
        )
        response = self.client.delete(f'/api/locations/{loc.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Location.objects.filter(id=loc.id).exists())


class ContactCRUDTestCase(AuthenticatedTestCase):
    """Test Contact CRUD operations."""

    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(name='Test Org', created_by=self.user)
        self.location = Location.objects.create(
            organization=self.org, name='Main Office', created_by=self.user
        )

    def test_create_contact(self):
        response = self.client.post('/api/contacts/', {
            'organization': str(self.org.id),
            'location': str(self.location.id),
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'title': 'IT Manager',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'Jane')
        self.assertEqual(response.data['full_name'], 'Jane Smith')

    def test_list_contacts(self):
        Contact.objects.create(
            organization=self.org, first_name='A', last_name='User',
            email='a@example.com', created_by=self.user
        )
        Contact.objects.create(
            organization=self.org, first_name='B', last_name='User',
            email='b@example.com', created_by=self.user
        )

        response = self.client.get('/api/contacts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 2)

    def test_update_contact(self):
        contact = Contact.objects.create(
            organization=self.org, first_name='Old', last_name='Name', created_by=self.user
        )
        response = self.client.patch(f'/api/contacts/{contact.id}/', {
            'first_name': 'New',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contact.refresh_from_db()
        self.assertEqual(contact.first_name, 'New')

    def test_filter_contacts_by_location(self):
        other_loc = Location.objects.create(
            organization=self.org, name='Branch', created_by=self.user
        )
        Contact.objects.create(
            organization=self.org, location=self.location,
            first_name='A', last_name='User', email='a@example.com',
            created_by=self.user
        )
        Contact.objects.create(
            organization=self.org, location=other_loc,
            first_name='B', last_name='User', email='b@example.com',
            created_by=self.user
        )

        response = self.client.get('/api/contacts/by_location/', {
            'location_id': str(self.location.id)
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['first_name'], 'A')


class DocumentationCRUDTestCase(AuthenticatedTestCase):
    """Test Documentation CRUD operations."""

    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(name='Test Org', created_by=self.user)

    def test_create_documentation(self):
        response = self.client.post('/api/documentations/', {
            'organization': str(self.org.id),
            'title': 'Setup Guide',
            'content': 'Step 1: Install...',
            'category': 'procedure',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Setup Guide')

    def test_list_documentations(self):
        Documentation.objects.create(
            organization=self.org, title='Doc A', content='Content A',
            created_by=self.user
        )
        response = self.client.get('/api/documentations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_update_documentation(self):
        doc = Documentation.objects.create(
            organization=self.org, title='Old Title', content='Old Content',
            created_by=self.user
        )
        response = self.client.patch(f'/api/documentations/{doc.id}/', {
            'title': 'Updated Title',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doc.refresh_from_db()
        self.assertEqual(doc.title, 'Updated Title')


class NetworkDeviceCRUDTestCase(AuthenticatedTestCase):
    """Test NetworkDevice CRUD operations."""

    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(name='Test Org', created_by=self.user)
        self.location = Location.objects.create(
            organization=self.org, name='DC', created_by=self.user
        )

    def test_create_network_device(self):
        response = self.client.post('/api/network-devices/', {
            'organization': str(self.org.id),
            'location': str(self.location.id),
            'name': 'Core Switch',
            'device_type': 'switch',
            'manufacturer': 'Cisco',
            'model': 'Catalyst 9300',
            'ip_address': '10.0.0.1',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Core Switch')

    def test_list_network_devices(self):
        NetworkDevice.objects.create(
            organization=self.org, name='FW-01', device_type='firewall',
            created_by=self.user
        )
        response = self.client.get('/api/network-devices/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class ServerCRUDTestCase(AuthenticatedTestCase):
    """Test Server CRUD operations."""

    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(name='Test Org', created_by=self.user)

    def test_create_server(self):
        response = self.client.post('/api/servers/', {
            'organization': str(self.org.id),
            'name': 'SRV-DB-01',
            'server_type': 'physical',
            'role': 'Database Server',
            'operating_system': 'Ubuntu 22.04',
            'ip_address': '192.168.1.10',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'SRV-DB-01')

    def test_list_servers(self):
        Server.objects.create(
            organization=self.org, name='SRV-01', server_type='physical',
            created_by=self.user
        )
        response = self.client.get('/api/servers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class EndpointUserCRUDTestCase(AuthenticatedTestCase):
    """Test EndpointUser (workstation) CRUD operations."""

    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(name='Test Org', created_by=self.user)

    def test_create_endpoint(self):
        response = self.client.post('/api/endpoint-users/', {
            'organization': str(self.org.id),
            'name': 'DESK-001',
            'device_type': 'desktop',
            'manufacturer': 'Dell',
            'model': 'OptiPlex 7090',
            'operating_system': 'Windows 11 Pro',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'DESK-001')

    def test_list_endpoints(self):
        EndpointUser.objects.create(
            organization=self.org, name='DESK-001', device_type='desktop',
            created_by=self.user
        )
        response = self.client.get('/api/endpoint-users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class PeripheralCRUDTestCase(AuthenticatedTestCase):
    """Test Peripheral CRUD operations."""

    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(name='Test Org', created_by=self.user)

    def test_create_peripheral(self):
        response = self.client.post('/api/peripherals/', {
            'organization': str(self.org.id),
            'name': 'Office Printer',
            'device_type': 'printer',
            'manufacturer': 'HP',
            'model': 'LaserJet Pro',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Office Printer')


class SoftwareCRUDTestCase(AuthenticatedTestCase):
    """Test Software CRUD with assignments."""

    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(name='Test Org', created_by=self.user)
        self.contact = Contact.objects.create(
            organization=self.org, first_name='John', last_name='Doe',
            created_by=self.user
        )

    def test_create_software(self):
        response = self.client.post('/api/software/', {
            'organization': str(self.org.id),
            'name': 'Adobe CC',
            'software_type': 'other',
            'license_type': 'subscription',
            'quantity': 10,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Adobe CC')

    def test_create_software_with_assignment(self):
        response = self.client.post('/api/software/', {
            'organization': str(self.org.id),
            'name': 'Adobe CC',
            'software_type': 'other',
            'license_type': 'subscription',
            'quantity': 10,
            'assigned_contact_ids': [str(self.contact.id)],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        sw = Software.objects.get(name='Adobe CC')
        self.assertEqual(sw.software_assignments.count(), 1)

    def test_list_software(self):
        Software.objects.create(
            organization=self.org, name='SW1', software_type='other',
            license_type='perpetual', created_by=self.user
        )
        response = self.client.get('/api/software/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class VoIPCRUDTestCase(AuthenticatedTestCase):
    """Test VoIP CRUD with assignments."""

    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(name='Test Org', created_by=self.user)
        self.contact = Contact.objects.create(
            organization=self.org, first_name='John', last_name='Doe',
            created_by=self.user
        )

    def test_create_voip(self):
        response = self.client.post('/api/voip/', {
            'organization': str(self.org.id),
            'name': 'Teams Phone',
            'voip_type': 'teams',
            'license_type': 'subscription',
            'quantity': 10,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Teams Phone')

    def test_create_voip_with_assignment(self):
        response = self.client.post('/api/voip/', {
            'organization': str(self.org.id),
            'name': 'Teams Phone',
            'voip_type': 'teams',
            'license_type': 'subscription',
            'quantity': 10,
            'assigned_contact_ids': [str(self.contact.id)],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        voip = VoIP.objects.get(name='Teams Phone')
        self.assertEqual(voip.voip_assignments.count(), 1)


class BackupCRUDTestCase(AuthenticatedTestCase):
    """Test Backup (infrastructure monitoring) CRUD operations."""

    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(name='Test Org', created_by=self.user)

    def test_create_backup(self):
        response = self.client.post('/api/backups/', {
            'organization': str(self.org.id),
            'name': 'Veeam Backup',
            'backup_type': 'server',
            'vendor': 'Veeam',
            'frequency': 'Daily',
            'backup_status': 'active',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Veeam Backup')

    def test_list_backups(self):
        Backup.objects.create(
            organization=self.org, name='BK1', backup_type='server',
            created_by=self.user
        )
        response = self.client.get('/api/backups/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class ConfigurationCRUDTestCase(AuthenticatedTestCase):
    """Test Configuration CRUD operations."""

    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(name='Test Org', created_by=self.user)

    def test_create_configuration(self):
        response = self.client.post('/api/configurations/', {
            'organization': str(self.org.id),
            'name': 'Firewall Rules',
            'config_type': 'security',
            'content': 'allow tcp 443',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Firewall Rules')

    def test_update_configuration(self):
        config = Configuration.objects.create(
            organization=self.org, name='FW Rules', config_type='security',
            content='old rules', created_by=self.user
        )
        response = self.client.patch(f'/api/configurations/{config.id}/', {
            'content': 'new rules',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        config.refresh_from_db()
        self.assertEqual(config.content, 'new rules')
