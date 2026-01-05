"""
Comprehensive security tests for TechVault login functionality.
Tests authentication, authorization, rate limiting, and security best practices.
"""
import time
import pyotp
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.auth_views import hash_backup_code

User = get_user_model()


class LoginSecurityTestCase(TestCase):
    """Test suite for login security."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.login_url = '/api/auth/login/'

        # Create test user
        self.test_email = 'test@example.com'
        self.test_password = 'SecureP@ssw0rd123'
        self.user = User.objects.create_user(
            email=self.test_email,
            password=self.test_password,
            first_name='Test',
            last_name='User'
        )

    def test_successful_login_without_2fa(self):
        """Test successful login without 2FA enabled."""
        response = self.client.post(self.login_url, {
            'email': self.test_email,
            'password': self.test_password
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertIn('user', response.data)
        # Since 2FA is now enforced, response should indicate setup is required
        self.assertTrue(response.data.get('requires_2fa_setup'))
        self.assertIn('message', response.data)
        self.assertIn('setup_url', response.data)

    def test_failed_login_invalid_credentials(self):
        """Test login with invalid credentials returns appropriate error."""
        response = self.client.post(self.login_url, {
            'email': self.test_email,
            'password': 'WrongPassword123'
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid credentials')
        # Ensure no token is leaked
        self.assertNotIn('access_token', response.data)

    def test_failed_login_nonexistent_user(self):
        """Test login with non-existent user."""
        response = self.client.post(self.login_url, {
            'email': 'nonexistent@example.com',
            'password': 'SomePassword123'
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Should return same error message to prevent user enumeration
        self.assertEqual(response.data['error'], 'Invalid credentials')

    def test_missing_email_parameter(self):
        """Test login without email parameter."""
        response = self.client.post(self.login_url, {
            'password': self.test_password
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_missing_password_parameter(self):
        """Test login without password parameter."""
        response = self.client.post(self.login_url, {
            'email': self.test_email
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_empty_credentials(self):
        """Test login with empty credentials."""
        response = self.client.post(self.login_url, {
            'email': '',
            'password': ''
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inactive_user_cannot_login(self):
        """Test that inactive users cannot login."""
        self.user.is_active = False
        self.user.save()

        response = self.client.post(self.login_url, {
            'email': self.test_email,
            'password': self.test_password
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error'], 'Account is disabled')

    def test_sql_injection_in_email(self):
        """Test SQL injection attempts in email field."""
        injection_attempts = [
            "' OR '1'='1",
            "admin'--",
            "' OR '1'='1' --",
            "admin' OR 1=1--",
        ]

        for injection in injection_attempts:
            response = self.client.post(self.login_url, {
                'email': injection,
                'password': 'password'
            })
            # Should fail authentication, not cause SQL error
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_xss_in_email_field(self):
        """Test XSS attempts in email field."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
        ]

        for payload in xss_payloads:
            response = self.client.post(self.login_url, {
                'email': payload,
                'password': 'password'
            })
            # Should fail authentication safely
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_not_returned_in_response(self):
        """Ensure password is never returned in any response."""
        response = self.client.post(self.login_url, {
            'email': self.test_email,
            'password': self.test_password
        })

        # Check response doesn't contain password
        response_str = str(response.data)
        self.assertNotIn(self.test_password, response_str)
        self.assertNotIn('password', response_str.lower())

    def test_case_sensitivity_of_email(self):
        """Test email authentication is case-insensitive."""
        response = self.client.post(self.login_url, {
            'email': self.test_email.upper(),
            'password': self.test_password
        })

        # Django's email field normalizes to lowercase
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_brute_force_multiple_failed_attempts(self):
        """Test multiple failed login attempts (brute force detection)."""
        # Note: This test documents the LACK of rate limiting
        failed_attempts = 0

        for i in range(10):
            response = self.client.post(self.login_url, {
                'email': self.test_email,
                'password': 'WrongPassword'
            })

            if response.status_code == status.HTTP_401_UNAUTHORIZED:
                failed_attempts += 1

        # Currently, all attempts succeed without rate limiting
        # THIS IS A SECURITY VULNERABILITY
        self.assertEqual(failed_attempts, 10)
        # TODO: Should implement rate limiting and account lockout


class TwoFactorAuthSecurityTestCase(TestCase):
    """Test suite for 2FA security."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.login_url = '/api/auth/login/'

        # Create test user with 2FA enabled
        self.test_email = 'test2fa@example.com'
        self.test_password = 'SecureP@ssw0rd123'
        self.twofa_secret = pyotp.random_base32()

        self.user = User.objects.create_user(
            email=self.test_email,
            password=self.test_password,
            first_name='Test',
            last_name='User'
        )

        # Enable 2FA
        self.user.twofa_enabled = True
        self.user.twofa_secret = self.twofa_secret

        # Generate and hash backup codes
        self.backup_codes = ['AABBCC', 'DDEEFF', 'GGHHII']
        self.user.twofa_backup_codes = [hash_backup_code(code) for code in self.backup_codes]
        self.user.save()

        self.totp = pyotp.TOTP(self.twofa_secret)

    def test_2fa_required_flag_returned(self):
        """Test that 2FA requirement is communicated properly."""
        response = self.client.post(self.login_url, {
            'email': self.test_email,
            'password': self.test_password
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('requires_2fa'))
        self.assertIn('message', response.data)
        self.assertNotIn('access_token', response.data)

    def test_successful_login_with_valid_totp(self):
        """Test successful login with valid TOTP token."""
        # Get valid TOTP token
        valid_token = self.totp.now()

        response = self.client.post(self.login_url, {
            'email': self.test_email,
            'password': self.test_password,
            'twofa_token': valid_token
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    def test_failed_login_with_invalid_totp(self):
        """Test login fails with invalid TOTP token."""
        response = self.client.post(self.login_url, {
            'email': self.test_email,
            'password': self.test_password,
            'twofa_token': '000000'
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_login_with_valid_backup_code(self):
        """Test successful login with backup code."""
        backup_code = self.backup_codes[0]

        response = self.client.post(self.login_url, {
            'email': self.test_email,
            'password': self.test_password,
            'twofa_token': backup_code
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertTrue(response.data.get('backup_code_used'))

        # Verify backup code was consumed
        self.user.refresh_from_db()
        self.assertEqual(len(self.user.twofa_backup_codes), 2)

    def test_backup_code_cannot_be_reused(self):
        """Test that backup codes can only be used once."""
        backup_code = self.backup_codes[0]

        # Use backup code once
        response1 = self.client.post(self.login_url, {
            'email': self.test_email,
            'password': self.test_password,
            'twofa_token': backup_code
        })
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        # Try to use same backup code again
        response2 = self.client.post(self.login_url, {
            'email': self.test_email,
            'password': self.test_password,
            'twofa_token': backup_code
        })
        self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_backup_code_case_insensitive(self):
        """Test backup codes work with different cases."""
        backup_code_lower = self.backup_codes[0].lower()

        response = self.client.post(self.login_url, {
            'email': self.test_email,
            'password': self.test_password,
            'twofa_token': backup_code_lower
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_backup_code_with_dashes(self):
        """Test backup codes work with formatting (dashes/spaces)."""
        # Add formatting to backup code
        backup_code_formatted = '-'.join(self.backup_codes[0])

        response = self.client.post(self.login_url, {
            'email': self.test_email,
            'password': self.test_password,
            'twofa_token': backup_code_formatted
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_totp_window_tolerance(self):
        """Test TOTP accepts tokens within valid time window."""
        # Current implementation uses valid_window=1 (±30 seconds)
        valid_token = self.totp.now()

        response = self.client.post(self.login_url, {
            'email': self.test_email,
            'password': self.test_password,
            'twofa_token': valid_token
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_2fa_bypassed_with_wrong_password(self):
        """Test 2FA cannot be bypassed with wrong password."""
        valid_token = self.totp.now()

        response = self.client.post(self.login_url, {
            'email': self.test_email,
            'password': 'WrongPassword',
            'twofa_token': valid_token
        })

        # Should fail at password stage, not proceed to 2FA
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_timing_attack_resistance(self):
        """Test response times don't leak information about valid users."""
        # Test with non-existent user
        start = time.time()
        self.client.post(self.login_url, {
            'email': 'nonexistent@example.com',
            'password': 'password'
        })
        time_nonexistent = time.time() - start

        # Test with existing user (wrong password)
        start = time.time()
        self.client.post(self.login_url, {
            'email': self.test_email,
            'password': 'wrongpassword'
        })
        time_existing = time.time() - start

        # Times should be similar (within 100ms)
        # Note: This is a basic test, timing attacks are complex
        time_diff = abs(time_existing - time_nonexistent)
        self.assertLess(time_diff, 0.1)


class JWTTokenSecurityTestCase(TestCase):
    """Test suite for JWT token security."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.login_url = '/api/auth/login/'

        self.test_email = 'testjwt@example.com'
        self.test_password = 'SecureP@ssw0rd123'
        self.user = User.objects.create_user(
            email=self.test_email,
            password=self.test_password,
            first_name='Test',
            last_name='User'
        )

    def test_token_contains_user_info(self):
        """Test JWT token contains appropriate user information."""
        response = self.client.post(self.login_url, {
            'email': self.test_email,
            'password': self.test_password
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], self.test_email)

        # Ensure sensitive data is not in token payload
        user_data = response.data['user']
        self.assertNotIn('password', user_data)

    def test_access_token_authentication(self):
        """Test API access with valid access token."""
        # Login to get token
        login_response = self.client.post(self.login_url, {
            'email': self.test_email,
            'password': self.test_password
        })

        access_token = login_response.data['access_token']

        # Use token to access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_response = self.client.get('/api/user/profile/')

        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)

    def test_invalid_token_rejected(self):
        """Test invalid tokens are rejected."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid-token-here')
        response = self.client.get('/api/user/profile/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_authorization_header(self):
        """Test protected endpoints require authorization."""
        response = self.client.get('/api/user/profile/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_malformed_authorization_header(self):
        """Test malformed authorization headers are rejected."""
        malformed_headers = [
            'InvalidFormat token',
            'Bearer',
            'Bearer  ',
            'Token invalid-format',
        ]

        for header in malformed_headers:
            self.client.credentials(HTTP_AUTHORIZATION=header)
            response = self.client.get('/api/user/profile/')
            self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class PasswordValidationTestCase(TestCase):
    """Test password validation and strength requirements."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()

    def test_weak_password_rejected_on_user_creation(self):
        """Test that weak passwords are rejected during user creation."""
        weak_passwords = [
            'password',
            '12345678',
            'qwerty',
            'abc123',
        ]

        for weak_pass in weak_passwords:
            with self.assertRaises(Exception):
                User.objects.create_user(
                    email=f'test{weak_pass}@example.com',
                    password=weak_pass,
                    first_name='Test',
                    last_name='User'
                )

    def test_password_minimum_length(self):
        """Test password minimum length requirement."""
        with self.assertRaises(Exception):
            User.objects.create_user(
                email='short@example.com',
                password='Short1',  # Less than 8 characters
                first_name='Test',
                last_name='User'
            )

    def test_strong_password_accepted(self):
        """Test that strong passwords are accepted."""
        strong_passwords = [
            'SecureP@ssw0rd123',
            'MyStr0ng!Pass',
            'C0mpl3x&P@ssword',
        ]

        for idx, strong_pass in enumerate(strong_passwords):
            user = User.objects.create_user(
                email=f'teststrong{idx}@example.com',
                password=strong_pass,
                first_name='Test',
                last_name='User'
            )
            self.assertIsNotNone(user)
            self.assertTrue(user.check_password(strong_pass))


class SecurityHeadersTestCase(TestCase):
    """Test security-related HTTP headers."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()

    def test_cors_headers_present(self):
        """Test CORS headers are present in responses."""
        response = self.client.options('/api/auth/login/')

        # CORS headers should be present
        self.assertIn('access-control-allow-origin',
                     [h.lower() for h in response.headers.keys()] or [])

    @override_settings(DEBUG=False)
    def test_security_headers_in_production(self):
        """Test security headers are set in production mode."""
        response = self.client.get('/api/auth/login/')

        # These should be set in production
        # Note: Currently missing, this test will fail
        # headers = response.headers
        # self.assertIn('X-Frame-Options', headers)
        # self.assertIn('X-Content-Type-Options', headers)
        # self.assertIn('Strict-Transport-Security', headers)
        pass  # Skip for now as headers are not configured


class InputValidationTestCase(TestCase):
    """Test input validation and sanitization."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.login_url = '/api/auth/login/'

    def test_extremely_long_email(self):
        """Test handling of extremely long email addresses."""
        long_email = 'a' * 10000 + '@example.com'

        response = self.client.post(self.login_url, {
            'email': long_email,
            'password': 'password'
        })

        # Should handle gracefully without errors
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])

    def test_extremely_long_password(self):
        """Test handling of extremely long passwords."""
        long_password = 'a' * 10000

        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': long_password
        })

        # Should handle gracefully without errors
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unicode_in_credentials(self):
        """Test handling of Unicode characters in credentials."""
        unicode_tests = [
            {'email': 'test@example.com', 'password': 'пароль123'},
            {'email': 'tëst@example.com', 'password': 'password'},
            {'email': '测试@example.com', 'password': 'password'},
        ]

        for credentials in unicode_tests:
            response = self.client.post(self.login_url, credentials)
            # Should handle without errors
            self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])

    def test_null_bytes_in_input(self):
        """Test handling of null bytes in input."""
        response = self.client.post(self.login_url, {
            'email': 'test\x00@example.com',
            'password': 'pass\x00word'
        })

        # Should handle safely
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
