"""
Tests for dashboard stats, diagram data, endpoint counts, and choices APIs.

Tests cover:
- Dashboard stats returns correct counts
- Endpoint counts requires organization_id
- Endpoint counts returns correct per-org counts
- Diagram data returns serialized device data
- Diagram data supports org and location filtering
- Choices endpoint returns valid choices
- System health endpoint requires admin
"""
import pyotp
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from core.models import (
    Organization, Location, Contact, Documentation,
    PasswordEntry, Configuration, NetworkDevice, EndpointUser,
    Server, Peripheral, Software, Backup, VoIP,
)

User = get_user_model()


class DashboardStatsTestCase(TestCase):
    """Test the dashboard stats API endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='SecureP@ssw0rd123',
            first_name='Test',
            last_name='User',
        )
        self.user.twofa_enabled = True
        self.user.twofa_secret = pyotp.random_base32()
        self.user.save()
        self.client.force_authenticate(user=self.user)

        self.org = Organization.objects.create(name='Test Org', created_by=self.user)

    def test_dashboard_stats_returns_counts(self):
        """Dashboard stats should return counts for all entity types."""
        Location.objects.create(organization=self.org, name='Office', created_by=self.user)
        Contact.objects.create(
            organization=self.org, first_name='J', last_name='D', created_by=self.user
        )

        response = self.client.get('/api/dashboard/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['organizations'], 1)
        self.assertEqual(response.data['locations'], 1)
        self.assertEqual(response.data['contacts'], 1)
        # All entity types should be present
        expected_keys = [
            'organizations', 'locations', 'contacts', 'documentations',
            'passwords', 'configurations', 'network_devices', 'endpoint_users',
            'servers', 'peripherals',
        ]
        for key in expected_keys:
            self.assertIn(key, response.data)

    def test_dashboard_stats_requires_auth(self):
        """Dashboard stats should require authentication."""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/dashboard/stats/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dashboard_stats_excludes_soft_deleted(self):
        """Dashboard stats should not count soft-deleted items."""
        loc = Location.objects.create(
            organization=self.org, name='Deleted', created_by=self.user
        )
        loc.delete(user=self.user)

        response = self.client.get('/api/dashboard/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['locations'], 0)


class EndpointCountsTestCase(TestCase):
    """Test the endpoint counts API."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='SecureP@ssw0rd123',
            first_name='Test',
            last_name='User',
        )
        self.user.twofa_enabled = True
        self.user.twofa_secret = pyotp.random_base32()
        self.user.save()
        self.client.force_authenticate(user=self.user)

        self.org = Organization.objects.create(name='Test Org', created_by=self.user)

    def test_endpoint_counts_requires_organization_id(self):
        """Should return 400 if organization_id is missing."""
        response = self.client.get('/api/endpoints/counts/')
        self.assertEqual(response.status_code, 400)
        self.assertIn('organization_id', response.data['error'])

    def test_endpoint_counts_returns_correct_counts(self):
        """Should return correct counts for each endpoint type."""
        NetworkDevice.objects.create(
            organization=self.org, name='FW-01', device_type='firewall',
            created_by=self.user
        )
        Server.objects.create(
            organization=self.org, name='SRV-01', server_type='physical',
            created_by=self.user
        )

        response = self.client.get('/api/endpoints/counts/', {
            'organization_id': str(self.org.id)
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['network_devices'], 1)
        self.assertEqual(response.data['servers'], 1)
        self.assertEqual(response.data['endpoint_users'], 0)
        expected_keys = [
            'network_devices', 'endpoint_users', 'servers', 'peripherals',
            'backups', 'software', 'voip',
        ]
        for key in expected_keys:
            self.assertIn(key, response.data)

    def test_endpoint_counts_filters_by_org(self):
        """Counts should only include items from the specified organization."""
        other_org = Organization.objects.create(name='Other Org', created_by=self.user)
        NetworkDevice.objects.create(
            organization=self.org, name='FW-01', device_type='firewall',
            created_by=self.user
        )
        NetworkDevice.objects.create(
            organization=other_org, name='FW-02', device_type='firewall',
            created_by=self.user
        )

        response = self.client.get('/api/endpoints/counts/', {
            'organization_id': str(self.org.id)
        })
        self.assertEqual(response.data['network_devices'], 1)


class DiagramDataTestCase(TestCase):
    """Test the diagram data API endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='SecureP@ssw0rd123',
            first_name='Test',
            last_name='User',
        )
        self.user.twofa_enabled = True
        self.user.twofa_secret = pyotp.random_base32()
        self.user.save()
        self.client.force_authenticate(user=self.user)

        self.org = Organization.objects.create(name='Test Org', created_by=self.user)
        self.location = Location.objects.create(
            organization=self.org, name='DC1', created_by=self.user
        )

    def test_diagram_data_returns_all_device_types(self):
        """Diagram data should return all device types."""
        NetworkDevice.objects.create(
            organization=self.org, location=self.location,
            name='FW-01', device_type='firewall', created_by=self.user
        )
        Server.objects.create(
            organization=self.org, location=self.location,
            name='SRV-01', server_type='physical', created_by=self.user
        )

        response = self.client.get('/api/diagram/data/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_keys = [
            'network_devices', 'endpoint_users', 'servers', 'peripherals',
            'backups', 'software', 'voip',
        ]
        for key in expected_keys:
            self.assertIn(key, response.data)
        self.assertEqual(len(response.data['network_devices']), 1)
        self.assertEqual(len(response.data['servers']), 1)

    def test_diagram_data_filters_by_organization(self):
        """Diagram data should filter by organization_id."""
        other_org = Organization.objects.create(name='Other', created_by=self.user)
        NetworkDevice.objects.create(
            organization=self.org, name='FW-01', device_type='firewall',
            created_by=self.user
        )
        NetworkDevice.objects.create(
            organization=other_org, name='FW-02', device_type='firewall',
            created_by=self.user
        )

        response = self.client.get('/api/diagram/data/', {
            'organization_id': str(self.org.id)
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['network_devices']), 1)

    def test_diagram_data_filters_by_location(self):
        """Diagram data should filter by location_id (includes unassigned)."""
        loc2 = Location.objects.create(
            organization=self.org, name='DC2', created_by=self.user
        )
        NetworkDevice.objects.create(
            organization=self.org, location=self.location,
            name='FW-01', device_type='firewall', created_by=self.user
        )
        NetworkDevice.objects.create(
            organization=self.org, location=loc2,
            name='FW-02', device_type='firewall', created_by=self.user
        )
        # Unassigned device (location=null)
        NetworkDevice.objects.create(
            organization=self.org, location=None,
            name='FW-03', device_type='firewall', created_by=self.user
        )

        response = self.client.get('/api/diagram/data/', {
            'organization_id': str(self.org.id),
            'location_id': str(self.location.id),
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should include FW-01 (matching location) and FW-03 (unassigned)
        self.assertEqual(len(response.data['network_devices']), 2)

    def test_diagram_data_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/diagram/data/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ChoicesAPITestCase(TestCase):
    """Test the meta choices endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='SecureP@ssw0rd123',
            first_name='Test',
            last_name='User',
        )
        self.user.twofa_enabled = True
        self.user.twofa_secret = pyotp.random_base32()
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_choices_returns_data(self):
        """Choices endpoint should return a dict of choice arrays."""
        response = self.client.get('/api/meta/choices/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        # Should have some choice categories
        self.assertGreater(len(response.data), 0)

    def test_choices_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/meta/choices/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SystemHealthTestCase(TestCase):
    """Test the system health endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='SecureP@ssw0rd123',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_superuser=True,
        )
        self.admin_user.twofa_enabled = True
        self.admin_user.twofa_secret = pyotp.random_base32()
        self.admin_user.save()

        self.regular_user = User.objects.create_user(
            email='regular@example.com',
            password='SecureP@ssw0rd123',
            first_name='Regular',
            last_name='User',
        )
        self.regular_user.twofa_enabled = True
        self.regular_user.twofa_secret = pyotp.random_base32()
        self.regular_user.save()

    def test_health_requires_admin(self):
        """System health should only be accessible to admin users."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get('/api/admin/health/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_health_returns_data_for_admin(self):
        """Admin users should get health data."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/admin/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('checks', response.data)
        self.assertIn('database', response.data['checks'])
        self.assertIn('users', response.data['checks'])
        self.assertIn('data', response.data['checks'])
