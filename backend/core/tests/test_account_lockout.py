"""
Tests for account lockout and user management functionality.

Tests cover:
- Account lockout after failed login attempts
- Lockout prevents login even with correct password
- Successful login resets failed attempt counter
- Lockout expires after timeout
- User profile retrieval and update
- User management admin-only access
- Admin cannot delete themselves
"""
import pyotp
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class AccountLockoutModelTestCase(TestCase):
    """Test the account lockout logic on the User model directly."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='locktest@example.com',
            password='TestP@ss123!',
            first_name='Lock',
            last_name='Test',
        )

    def test_initial_state_is_not_locked(self):
        self.assertFalse(self.user.is_locked())
        self.assertEqual(self.user.failed_login_attempts, 0)

    def test_record_failed_login_increments_counter(self):
        self.user.record_failed_login()
        self.assertEqual(self.user.failed_login_attempts, 1)
        self.assertIsNotNone(self.user.last_failed_login)

    def test_account_locks_after_max_attempts(self):
        for _ in range(5):
            self.user.record_failed_login()
        self.assertTrue(self.user.is_locked())
        self.assertIsNotNone(self.user.locked_until)

    def test_locked_account_returns_true(self):
        self.user.locked_until = timezone.now() + timedelta(minutes=15)
        self.user.save()
        self.assertTrue(self.user.is_locked())

    def test_expired_lockout_returns_false(self):
        self.user.locked_until = timezone.now() - timedelta(minutes=1)
        self.user.save()
        self.assertFalse(self.user.is_locked())

    def test_reset_failed_login_attempts(self):
        for _ in range(3):
            self.user.record_failed_login()
        self.assertEqual(self.user.failed_login_attempts, 3)

        self.user.reset_failed_login_attempts()
        self.assertEqual(self.user.failed_login_attempts, 0)
        self.assertIsNone(self.user.locked_until)
        self.assertIsNone(self.user.last_failed_login)


@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': [],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10000/minute',
        'user': '10000/minute',
        'login': '10000/minute',
        '2fa_verification': '10000/minute',
    },
})
class AccountLockoutAPITestCase(TestCase):
    """Test account lockout through the login API."""

    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.client = APIClient()
        self.login_url = '/api/auth/login/'
        self.password = 'SecureP@ss123!'

        self.user = User.objects.create_user(
            email='locktest@example.com',
            password=self.password,
            first_name='Lock',
            last_name='Test',
        )

    def test_login_with_locked_account_returns_403(self):
        """A locked account should return 403 even with correct credentials."""
        # Lock the account
        self.user.locked_until = timezone.now() + timedelta(minutes=15)
        self.user.failed_login_attempts = 5
        self.user.save()

        response = self.client.post(self.login_url, {
            'email': 'locktest@example.com',
            'password': self.password,
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_failed_login_increments_counter_via_api(self):
        """Failed login via API should increment the counter."""
        self.client.post(self.login_url, {
            'email': 'locktest@example.com',
            'password': 'WrongPassword!',
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.failed_login_attempts, 1)

    def test_multiple_failed_logins_lock_account(self):
        """5 failed logins should lock the account."""
        for _ in range(5):
            self.client.post(self.login_url, {
                'email': 'locktest@example.com',
                'password': 'WrongPassword!',
            })

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_locked())
        self.assertEqual(self.user.failed_login_attempts, 5)


class UserProfileTestCase(TestCase):
    """Test user profile API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='profile@example.com',
            password='SecureP@ss123!',
            first_name='Profile',
            last_name='User',
        )
        self.user.twofa_enabled = True
        self.user.twofa_secret = pyotp.random_base32()
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        response = self.client.get('/api/user/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'profile@example.com')
        self.assertEqual(response.data['first_name'], 'Profile')

    def test_update_profile(self):
        response = self.client.patch('/api/user/profile/', {
            'first_name': 'Updated',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')

    def test_profile_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/user/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserManagementTestCase(TestCase):
    """Test admin user management endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='SecureP@ss123!',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_superuser=True,
        )
        self.admin.twofa_enabled = True
        self.admin.twofa_secret = pyotp.random_base32()
        self.admin.save()

        self.regular = User.objects.create_user(
            email='regular@example.com',
            password='SecureP@ss123!',
            first_name='Regular',
            last_name='User',
        )
        self.regular.twofa_enabled = True
        self.regular.twofa_secret = pyotp.random_base32()
        self.regular.save()

    def test_list_users_requires_admin(self):
        self.client.force_authenticate(user=self.regular)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_cannot_delete_self(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/users/{self.admin.id}/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cannot delete your own', response.data['detail'].lower())

    def test_admin_can_delete_other_user(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/users/{self.regular.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(email='regular@example.com').exists())

    def test_create_user_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/users/', {
            'email': 'newuser@example.com',
            'password': 'NewP@ss123!',
            'first_name': 'New',
            'last_name': 'User',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
