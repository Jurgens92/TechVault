"""
Tests for soft delete and restore functionality.

Tests cover:
- Soft delete hides items from default queries
- Soft-deleted items are accessible via all_objects
- Restore brings items back
- Deleted items endpoint lists soft-deleted items
- Hard delete permanently removes items (admin only)
- Non-admin cannot hard delete
- Restoring a non-deleted item returns error
"""
import pyotp
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from users.auth_views import hash_backup_code

from core.models import (
    Organization, Location, Contact, Documentation,
    PasswordEntry, Configuration, NetworkDevice,
)

User = get_user_model()


class SoftDeleteTestCase(TestCase):
    """Test soft delete and restore through the API."""

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

        self.client.force_authenticate(user=self.admin_user)

        self.org = Organization.objects.create(
            name='Test Org', created_by=self.admin_user
        )

    def test_delete_organization_is_soft_delete(self):
        """DELETE should soft-delete, not hard-delete."""
        response = self.client.delete(f'/api/organizations/{self.org.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('deleted items', response.data['detail'].lower())

        # Not in default queryset
        self.assertFalse(Organization.objects.filter(id=self.org.id).exists())
        # Still in all_objects
        org = Organization.all_objects.get(id=self.org.id)
        self.assertIsNotNone(org.deleted_at)
        self.assertEqual(org.deleted_by, self.admin_user)

    def test_restore_soft_deleted_item(self):
        """Restore action should bring back a soft-deleted item."""
        self.org.delete(user=self.admin_user)
        self.assertFalse(Organization.objects.filter(id=self.org.id).exists())

        response = self.client.post(f'/api/organizations/{self.org.id}/restore/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('restored', response.data['detail'].lower())

        # Should be back in the default queryset
        self.assertTrue(Organization.objects.filter(id=self.org.id).exists())
        self.org.refresh_from_db()
        self.assertIsNone(self.org.deleted_at)

    def test_restore_non_deleted_item_returns_error(self):
        """Restoring an item that isn't deleted should return 400."""
        response = self.client.post(f'/api/organizations/{self.org.id}/restore/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_restore_nonexistent_item_returns_404(self):
        """Restoring a nonexistent item should return 404."""
        import uuid
        fake_id = uuid.uuid4()
        response = self.client.post(f'/api/organizations/{fake_id}/restore/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_deleted_items(self):
        """Deleted endpoint should list soft-deleted items."""
        org2 = Organization.objects.create(name='Org 2', created_by=self.admin_user)
        self.org.delete(user=self.admin_user)

        response = self.client.get('/api/organizations/deleted/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        deleted_names = [item['name'] for item in results]
        self.assertIn('Test Org', deleted_names)
        self.assertNotIn('Org 2', deleted_names)

    def test_hard_delete_permanently_removes(self):
        """Hard delete should permanently remove the item."""
        response = self.client.delete(f'/api/organizations/{self.org.id}/hard_delete/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Organization.all_objects.filter(id=self.org.id).exists())

    def test_hard_delete_requires_admin(self):
        """Non-staff users cannot hard delete."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(f'/api/organizations/{self.org.id}/hard_delete/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_soft_delete_location(self):
        """Test soft delete works on Location model."""
        loc = Location.objects.create(
            organization=self.org, name='Branch', created_by=self.admin_user
        )
        response = self.client.delete(f'/api/locations/{loc.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Location.objects.filter(id=loc.id).exists())
        self.assertTrue(Location.all_objects.filter(id=loc.id).exists())

    def test_soft_delete_contact(self):
        """Test soft delete works on Contact model."""
        contact = Contact.objects.create(
            organization=self.org, first_name='Jane', last_name='Doe',
            created_by=self.admin_user
        )
        response = self.client.delete(f'/api/contacts/{contact.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Contact.objects.filter(id=contact.id).exists())

    def test_soft_delete_documentation(self):
        """Test soft delete works on Documentation model."""
        doc = Documentation.objects.create(
            organization=self.org, title='Guide', content='...',
            created_by=self.admin_user
        )
        response = self.client.delete(f'/api/documentations/{doc.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Documentation.objects.filter(id=doc.id).exists())

    def test_soft_delete_network_device(self):
        """Test soft delete works on NetworkDevice model."""
        device = NetworkDevice.objects.create(
            organization=self.org, name='FW-01', device_type='firewall',
            created_by=self.admin_user
        )
        response = self.client.delete(f'/api/network-devices/{device.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(NetworkDevice.objects.filter(id=device.id).exists())

    def test_restore_location(self):
        """Test restore works on Location model."""
        loc = Location.objects.create(
            organization=self.org, name='Branch', created_by=self.admin_user
        )
        loc.delete(user=self.admin_user)

        response = self.client.post(f'/api/locations/{loc.id}/restore/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Location.objects.filter(id=loc.id).exists())
