"""
Tests for PasswordEntry API with encryption.

Tests cover:
- Creating password entries encrypts the password
- Listing password entries never exposes passwords
- Retrieving password via special action returns decrypted value
- Updating password re-encrypts
- Updating without password keeps existing password
- Password required on create
"""
import pyotp
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from users.auth_views import hash_backup_code

from core.models import Organization, PasswordEntry
from core.encryption import decrypt_password, is_encrypted

User = get_user_model()


class PasswordEntryAPITestCase(TestCase):
    """Test PasswordEntry API with encryption behavior."""

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

    def test_create_password_entry_encrypts_password(self):
        """Creating a password entry should encrypt the password in the database."""
        response = self.client.post('/api/passwords/', {
            'organization': str(self.org.id),
            'name': 'Server Admin',
            'username': 'admin',
            'password': 'MySecret123!',
            'category': 'device',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify password is encrypted in the database
        entry = PasswordEntry.objects.get(name='Server Admin')
        self.assertTrue(is_encrypted(entry.password))
        self.assertTrue(entry.is_encrypted)
        # Encrypted value should NOT equal the plaintext
        self.assertNotEqual(entry.password, 'MySecret123!')

    def test_list_passwords_never_exposes_password(self):
        """Listing password entries should never include the password field."""
        self.client.post('/api/passwords/', {
            'organization': str(self.org.id),
            'name': 'Test Entry',
            'username': 'admin',
            'password': 'Secret!',
            'category': 'device',
        })

        response = self.client.get('/api/passwords/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertGreaterEqual(len(results), 1)
        for entry in results:
            self.assertNotIn('password', entry)
            self.assertIn('has_password', entry)
            self.assertTrue(entry['has_password'])

    def test_retrieve_password_entry_no_password_field(self):
        """GET on a single password entry should not include password."""
        create_response = self.client.post('/api/passwords/', {
            'organization': str(self.org.id),
            'name': 'Test Entry',
            'username': 'admin',
            'password': 'Secret!',
            'category': 'device',
        })
        entry_id = create_response.data['id']

        response = self.client.get(f'/api/passwords/{entry_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('password', response.data)
        self.assertTrue(response.data['has_password'])

    def test_retrieve_password_action_returns_decrypted(self):
        """POST to retrieve_password action should return the decrypted password."""
        create_response = self.client.post('/api/passwords/', {
            'organization': str(self.org.id),
            'name': 'Firewall',
            'username': 'admin',
            'password': 'FW_Secret_2024!',
            'category': 'device',
        })
        entry_id = create_response.data['id']

        response = self.client.post(f'/api/passwords/{entry_id}/retrieve_password/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['password'], 'FW_Secret_2024!')
        self.assertIn('warning', response.data)

    def test_update_password_re_encrypts(self):
        """Updating the password should encrypt the new value."""
        create_response = self.client.post('/api/passwords/', {
            'organization': str(self.org.id),
            'name': 'Test',
            'username': 'admin',
            'password': 'OldPass!',
            'category': 'device',
        })
        entry_id = create_response.data['id']

        response = self.client.patch(f'/api/passwords/{entry_id}/', {
            'password': 'NewPass_2024!',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify new password is encrypted and correct
        entry = PasswordEntry.objects.get(id=entry_id)
        self.assertTrue(is_encrypted(entry.password))
        self.assertEqual(decrypt_password(entry.password), 'NewPass_2024!')

    def test_update_without_password_keeps_existing(self):
        """Updating other fields without password should keep existing password."""
        create_response = self.client.post('/api/passwords/', {
            'organization': str(self.org.id),
            'name': 'Test',
            'username': 'admin',
            'password': 'KeepThis!',
            'category': 'device',
        })
        entry_id = create_response.data['id']

        # Update only the name
        response = self.client.patch(f'/api/passwords/{entry_id}/', {
            'name': 'Updated Name',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify original password is preserved
        entry = PasswordEntry.objects.get(id=entry_id)
        self.assertEqual(decrypt_password(entry.password), 'KeepThis!')

    def test_update_with_empty_password_keeps_existing(self):
        """Updating with empty string password should keep existing password."""
        create_response = self.client.post('/api/passwords/', {
            'organization': str(self.org.id),
            'name': 'Test',
            'username': 'admin',
            'password': 'KeepThis!',
            'category': 'device',
        })
        entry_id = create_response.data['id']

        # Update with empty password
        response = self.client.patch(f'/api/passwords/{entry_id}/', {
            'password': '',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify original password is preserved
        entry = PasswordEntry.objects.get(id=entry_id)
        self.assertEqual(decrypt_password(entry.password), 'KeepThis!')

    def test_soft_delete_password_entry(self):
        """Soft deleting a password entry should hide it."""
        create_response = self.client.post('/api/passwords/', {
            'organization': str(self.org.id),
            'name': 'Delete Me',
            'username': 'admin',
            'password': 'Secret!',
            'category': 'device',
        })
        entry_id = create_response.data['id']

        response = self.client.delete(f'/api/passwords/{entry_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(PasswordEntry.objects.filter(id=entry_id).exists())
        self.assertTrue(PasswordEntry.all_objects.filter(id=entry_id).exists())
