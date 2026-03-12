"""
Tests for version history functionality.

Tests cover:
- Creating an entity creates an initial version
- Updating an entity creates a version before the update
- Version history lists all versions in descending order
- Retrieving a specific version returns correct data
- Restoring a version reverts the entity state
- Restoring a nonexistent version returns 404
- Version history for Documentation, PasswordEntry, and Configuration
"""
import pyotp
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from core.models import (
    Organization, Documentation, PasswordEntry, Configuration,
    EntityVersion,
)

User = get_user_model()


class VersionHistoryTestCase(TestCase):
    """Test version history through API endpoints."""

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

    def test_create_documentation_creates_version(self):
        """Creating a documentation should create an initial version."""
        response = self.client.post('/api/documentations/', {
            'organization': str(self.org.id),
            'title': 'Setup Guide',
            'content': 'Step 1: Install...',
            'category': 'procedure',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        doc_id = response.data['id']

        # Check version history - should have the initial version
        response = self.client.get(f'/api/documentations/{doc_id}/versions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_update_documentation_creates_version(self):
        """Updating documentation should create a version before the update."""
        # Create
        create_resp = self.client.post('/api/documentations/', {
            'organization': str(self.org.id),
            'title': 'Version 1 Title',
            'content': 'Version 1 Content',
            'category': 'procedure',
        })
        doc_id = create_resp.data['id']

        # Update
        self.client.patch(f'/api/documentations/{doc_id}/', {
            'title': 'Version 2 Title',
            'content': 'Version 2 Content',
        })

        # Check versions
        response = self.client.get(f'/api/documentations/{doc_id}/versions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should have at least 2 versions (initial + pre-update)
        self.assertGreaterEqual(len(response.data), 2)

    def test_get_specific_version(self):
        """Retrieving a specific version number should return that version's data."""
        create_resp = self.client.post('/api/documentations/', {
            'organization': str(self.org.id),
            'title': 'Original Title',
            'content': 'Original Content',
            'category': 'procedure',
        })
        doc_id = create_resp.data['id']

        response = self.client.get(f'/api/documentations/{doc_id}/versions/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['version_number'], 1)

    def test_get_nonexistent_version_returns_404(self):
        """Requesting a version that doesn't exist should return 404."""
        create_resp = self.client.post('/api/documentations/', {
            'organization': str(self.org.id),
            'title': 'Test Doc',
            'content': 'Content',
            'category': 'procedure',
        })
        doc_id = create_resp.data['id']

        response = self.client.get(f'/api/documentations/{doc_id}/versions/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_restore_version(self):
        """Restoring a version should revert the entity to that version's state."""
        # Create
        create_resp = self.client.post('/api/documentations/', {
            'organization': str(self.org.id),
            'title': 'Original Title',
            'content': 'Original Content',
            'category': 'procedure',
        })
        doc_id = create_resp.data['id']

        # Update to change the title
        self.client.patch(f'/api/documentations/{doc_id}/', {
            'title': 'Updated Title',
            'content': 'Updated Content',
        })

        # Verify it was updated
        doc = Documentation.objects.get(id=doc_id)
        self.assertEqual(doc.title, 'Updated Title')

        # Restore to version 1
        response = self.client.post(f'/api/documentations/{doc_id}/restore-version/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('restored', response.data['detail'].lower())

        # Verify it was reverted
        doc.refresh_from_db()
        self.assertEqual(doc.title, 'Original Title')

    def test_restore_nonexistent_version_returns_404(self):
        """Restoring a version that doesn't exist should return 404."""
        create_resp = self.client.post('/api/documentations/', {
            'organization': str(self.org.id),
            'title': 'Test Doc',
            'content': 'Content',
            'category': 'procedure',
        })
        doc_id = create_resp.data['id']

        response = self.client.post(f'/api/documentations/{doc_id}/restore-version/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_password_entry_version_history(self):
        """PasswordEntry should track version history."""
        create_resp = self.client.post('/api/passwords/', {
            'organization': str(self.org.id),
            'name': 'Server Admin',
            'username': 'admin',
            'password': 'Pass1!',
            'category': 'device',
        })
        entry_id = create_resp.data['id']

        # Update
        self.client.patch(f'/api/passwords/{entry_id}/', {
            'name': 'Updated Server Admin',
        })

        response = self.client.get(f'/api/passwords/{entry_id}/versions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_configuration_version_history(self):
        """Configuration should track version history."""
        create_resp = self.client.post('/api/configurations/', {
            'organization': str(self.org.id),
            'name': 'FW Rules',
            'config_type': 'security',
            'content': 'allow tcp 80',
        })
        config_id = create_resp.data['id']

        # Update
        self.client.patch(f'/api/configurations/{config_id}/', {
            'content': 'allow tcp 80\nallow tcp 443',
        })

        response = self.client.get(f'/api/configurations/{config_id}/versions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)
