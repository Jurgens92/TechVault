"""
Tests for 2FA enforcement middleware.

Tests that authenticated users without 2FA enabled are blocked from accessing
protected endpoints until they enable 2FA.
"""
import pyotp
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from users.auth_views import hash_backup_code

User = get_user_model()


class Enforce2FAMiddlewareTestCase(TestCase):
    """Test suite for 2FA enforcement middleware."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.login_url = '/api/auth/login/'

        # Create test user WITHOUT 2FA enabled
        self.test_email_no_2fa = 'no2fa@example.com'
        self.test_password = 'SecureP@ssw0rd123'
        self.user_no_2fa = User.objects.create_user(
            email=self.test_email_no_2fa,
            password=self.test_password,
            first_name='Test',
            last_name='User'
        )

        # Create test user WITH 2FA enabled
        self.test_email_with_2fa = 'with2fa@example.com'
        self.twofa_secret = pyotp.random_base32()
        self.user_with_2fa = User.objects.create_user(
            email=self.test_email_with_2fa,
            password=self.test_password,
            first_name='Test',
            last_name='User2FA'
        )
        self.user_with_2fa.twofa_enabled = True
        self.user_with_2fa.twofa_secret = self.twofa_secret
        self.user_with_2fa.twofa_backup_codes = [hash_backup_code('TESTCODE')]
        self.user_with_2fa.save()

        self.totp = pyotp.TOTP(self.twofa_secret)

    def test_login_response_includes_2fa_setup_requirement(self):
        """Test that login response indicates 2FA setup is required."""
        response = self.client.post(self.login_url, {
            'email': self.test_email_no_2fa,
            'password': self.test_password
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertTrue(response.data.get('requires_2fa_setup'))
        self.assertIn('message', response.data)
        self.assertIn('2FA', response.data['message'])
        self.assertIn('setup_url', response.data)

    def test_user_without_2fa_blocked_from_protected_endpoints(self):
        """Test that users without 2FA are blocked from accessing protected endpoints."""
        # Login to get token
        login_response = self.client.post(self.login_url, {
            'email': self.test_email_no_2fa,
            'password': self.test_password
        })
        access_token = login_response.data['access_token']

        # Try to access a protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # Test various protected endpoints
        protected_endpoints = [
            '/api/user/profile/',
            '/api/organizations/',
            '/api/devices/',
            '/api/servers/',
        ]

        for endpoint in protected_endpoints:
            response = self.client.get(endpoint)

            # Should be blocked with 403 Forbidden
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
                f"Endpoint {endpoint} should be blocked"
            )
            self.assertIn('error', response.data)
            self.assertIn('2FA', response.data['error'])
            self.assertTrue(response.data.get('requires_2fa_setup'))

    def test_user_without_2fa_can_access_2fa_setup_endpoints(self):
        """Test that users without 2FA can access 2FA setup endpoints."""
        # Login to get token
        login_response = self.client.post(self.login_url, {
            'email': self.test_email_no_2fa,
            'password': self.test_password
        })
        access_token = login_response.data['access_token']

        # Use token to access 2FA setup endpoints
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # These should be allowed
        allowed_endpoints = [
            '/api/auth/2fa/status/',
            '/api/auth/2fa/setup/',
        ]

        for endpoint in allowed_endpoints:
            response = self.client.get(endpoint) if endpoint.endswith('status/') else self.client.post(endpoint)

            # Should NOT be blocked by 2FA enforcement
            # (though may have other validation errors)
            self.assertNotEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
                f"Endpoint {endpoint} should be allowed for 2FA setup"
            )

    def test_user_with_2fa_can_access_all_endpoints(self):
        """Test that users with 2FA enabled can access all endpoints."""
        # Login with 2FA
        valid_token = self.totp.now()
        login_response = self.client.post(self.login_url, {
            'email': self.test_email_with_2fa,
            'password': self.test_password,
            'twofa_token': valid_token
        })

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertNotIn('requires_2fa_setup', login_response.data)

        access_token = login_response.data['access_token']

        # Use token to access protected endpoints
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # These should be allowed
        allowed_endpoints = [
            '/api/user/profile/',
            '/api/auth/2fa/status/',
            '/api/organizations/',
        ]

        for endpoint in allowed_endpoints:
            response = self.client.get(endpoint)

            # Should NOT be blocked by 2FA enforcement
            # May return 200 or 404 depending on data, but NOT 403 due to 2FA
            self.assertNotEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
                f"Endpoint {endpoint} should be accessible for users with 2FA"
            )

            # If it's 403, it shouldn't be about 2FA
            if response.status_code == status.HTTP_403_FORBIDDEN:
                self.assertNotIn('requires_2fa_setup', response.data)

    def test_user_without_2fa_can_logout(self):
        """Test that users without 2FA can logout."""
        # Login to get token
        login_response = self.client.post(self.login_url, {
            'email': self.test_email_no_2fa,
            'password': self.test_password
        })
        access_token = login_response.data['access_token']

        # Try to logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.post('/api/auth/logout/')

        # Should be allowed to logout
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_public_endpoints_not_affected(self):
        """Test that public endpoints are not affected by 2FA enforcement."""
        # These endpoints should work without authentication
        public_endpoints = [
            ('/api/auth/login/', 'POST'),
        ]

        for endpoint, method in public_endpoints:
            if method == 'POST':
                response = self.client.post(endpoint, {})
            else:
                response = self.client.get(endpoint)

            # Should not be blocked by 2FA middleware
            # (may have validation errors but not 403 from 2FA)
            self.assertNotIn(
                'requires_2fa_setup',
                response.data if hasattr(response, 'data') else {}
            )

    def test_unauthenticated_requests_not_affected(self):
        """Test that unauthenticated requests are not affected by middleware."""
        # Clear credentials
        self.client.credentials()

        # Try to access protected endpoint without auth
        response = self.client.get('/api/user/profile/')

        # Should get 401 Unauthorized, not 403 from 2FA enforcement
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('requires_2fa_setup', response.data if hasattr(response, 'data') else {})

    def test_user_can_enable_2fa_and_then_access_endpoints(self):
        """Test the full flow: login without 2FA, enable 2FA, then access endpoints."""
        # Step 1: Login without 2FA
        login_response = self.client.post(self.login_url, {
            'email': self.test_email_no_2fa,
            'password': self.test_password
        })
        access_token = login_response.data['access_token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # Step 2: Verify blocked from protected endpoints
        response = self.client.get('/api/organizations/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Step 3: Setup 2FA
        setup_response = self.client.post('/api/auth/2fa/setup/')
        self.assertEqual(setup_response.status_code, status.HTTP_200_OK)
        secret = setup_response.data['secret']

        # Step 4: Enable 2FA
        totp = pyotp.TOTP(secret)
        enable_response = self.client.post('/api/auth/2fa/enable/', {
            'token': totp.now()
        })
        self.assertEqual(enable_response.status_code, status.HTTP_200_OK)

        # Step 5: Now should be able to access protected endpoints
        response = self.client.get('/api/organizations/')
        # Should NOT be blocked by 2FA (may be 200 or other status, but not 403 from 2FA)
        if response.status_code == status.HTTP_403_FORBIDDEN:
            self.assertNotIn('requires_2fa_setup', response.data)
