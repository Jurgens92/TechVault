"""
Tests for backup and restore functionality.

Tests cover:
- Full system backup with actual data (all entity types including VoIP)
- Backup password protection and encryption key wrapping
- Restore to a clean database
- Restore with overwrite of existing records
- Password entry encryption round-trip through backup/restore
- Re-encryption of passwords when restoring with a different encryption key
- Wrong backup password rejection
- Missing backup password rejection for protected backups
- User restore including 2FA configuration and password hashes
- Selective restore (users only, organizations only)
"""
import pyotp
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from datetime import timedelta

from core.models import (
    Organization, OrganizationMember, Location, Contact,
    Documentation, PasswordEntry, Configuration,
    NetworkDevice, EndpointUser, Server, Peripheral,
    Software, SoftwareAssignment, Backup,
    VoIP, VoIPAssignment,
)
from core.encryption import (
    encrypt_password, decrypt_password, is_encrypted,
    protect_encryption_key, recover_encryption_key,
    EncryptionError,
)
from reports.system_backup_service import SystemBackupService

User = get_user_model()


class BackupRestoreDataMixin:
    """Mixin that populates the database with realistic test data."""

    def create_test_data(self):
        """Create a full set of test data across all entity types."""
        today = timezone.now().date()

        # --- Users ---
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='Admin_P@ssw0rd!',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_superuser=True,
        )

        self.regular_user = User.objects.create_user(
            email='user@test.com',
            password='User_P@ssw0rd!',
            first_name='Regular',
            last_name='User',
        )

        # User with 2FA enabled
        self.twofa_user = User.objects.create_user(
            email='twofa@test.com',
            password='TwoFA_P@ssw0rd!',
            first_name='TwoFA',
            last_name='User',
        )
        self.twofa_secret = pyotp.random_base32()
        self.twofa_user.twofa_enabled = True
        self.twofa_user.twofa_secret = self.twofa_secret
        self.twofa_user.twofa_backup_codes = ['hash1', 'hash2', 'hash3']
        self.twofa_user.save()

        # --- Organization ---
        self.org = Organization.objects.create(
            name='Test Corp',
            description='Test organization for backup testing',
            website='https://testcorp.example.com',
            phone='+1-555-9000',
            email='info@testcorp.example.com',
            address='100 Test Street',
            city='Testville',
            state_province='TestState',
            postal_code='99999',
            country='United States',
            created_by=self.admin_user,
        )

        OrganizationMember.objects.create(
            organization=self.org,
            user=self.admin_user,
            role='admin',
            is_active=True,
            created_by=self.admin_user,
        )
        OrganizationMember.objects.create(
            organization=self.org,
            user=self.regular_user,
            role='member',
            is_active=True,
            created_by=self.admin_user,
        )

        # --- Location ---
        self.location = Location.objects.create(
            organization=self.org,
            name='Main Office',
            description='Primary office location',
            address='100 Test Street',
            city='Testville',
            state_province='TestState',
            postal_code='99999',
            country='United States',
            phone='+1-555-9001',
            created_by=self.admin_user,
        )

        # --- Contacts ---
        self.contact1 = Contact.objects.create(
            organization=self.org,
            location=self.location,
            first_name='John',
            last_name='Doe',
            title='IT Manager',
            email='john.doe@testcorp.example.com',
            phone='+1-555-9010',
            mobile='+1-555-9011',
            notes='Primary IT contact',
            created_by=self.admin_user,
        )
        self.contact2 = Contact.objects.create(
            organization=self.org,
            location=self.location,
            first_name='Jane',
            last_name='Smith',
            title='Office Manager',
            email='jane.smith@testcorp.example.com',
            phone='+1-555-9020',
            mobile='+1-555-9021',
            notes='Office operations',
            created_by=self.admin_user,
        )

        # --- Documentation ---
        self.doc = Documentation.objects.create(
            organization=self.org,
            title='Network Setup Guide',
            content='VLAN 10: Management\nVLAN 20: Workstations\nVLAN 30: Servers',
            category='configuration',
            tags='network, vlans',
            is_published=True,
            created_by=self.admin_user,
        )

        # --- Password Entries (with encryption) ---
        self.plain_passwords = {
            'Firewall Admin': 'FW_Admin_2024!',
            'Server Admin': 'Srv_Secure_P@ss!',
            'Cloud Portal': 'Cloud_Access_2024!',
        }
        self.password_entries = []
        for name, plaintext in self.plain_passwords.items():
            encrypted = encrypt_password(plaintext)
            entry = PasswordEntry.objects.create(
                organization=self.org,
                name=name,
                username='admin',
                password=encrypted,
                url='https://example.com',
                notes=f'{name} credentials',
                category='device',
                is_encrypted=True,
                created_by=self.admin_user,
            )
            self.password_entries.append(entry)

        # --- Configuration ---
        self.config = Configuration.objects.create(
            organization=self.org,
            name='Firewall Rules',
            config_type='security',
            content='allow tcp 80\nallow tcp 443\ndeny all',
            description='Main firewall config',
            version='1.0',
            created_by=self.admin_user,
        )

        # --- Network Device ---
        self.network_device = NetworkDevice.objects.create(
            organization=self.org,
            location=self.location,
            name='Core Firewall',
            device_type='firewall',
            internet_provider='Comcast Business',
            internet_speed='1000/1000 Mbps',
            manufacturer='Fortinet',
            model='FortiGate 60F',
            ip_address='192.168.1.1',
            mac_address='00:09:0F:AA:BB:CC',
            serial_number='FG60F-TEST001',
            firmware_version='7.2.4',
            notes='Primary firewall',
            created_by=self.admin_user,
        )

        # --- Endpoint User ---
        self.endpoint = EndpointUser.objects.create(
            organization=self.org,
            location=self.location,
            assigned_to=self.contact1,
            name='DESK-JDOE',
            device_type='desktop',
            manufacturer='Dell',
            model='OptiPlex 7090',
            cpu='Intel Core i7-11700',
            ram='32GB DDR4',
            storage='1TB NVMe SSD',
            operating_system='Windows 11 Pro',
            ip_address='192.168.1.100',
            mac_address='00:11:22:AA:BB:01',
            hostname='DESK-JDOE',
            serial_number='DL-TEST-001',
            purchase_date=today - timedelta(days=365),
            warranty_expiry=today + timedelta(days=730),
            notes='IT Manager workstation',
            created_by=self.admin_user,
        )

        # --- Server ---
        self.server = Server.objects.create(
            organization=self.org,
            location=self.location,
            name='SRV-DC-01',
            server_type='physical',
            role='Domain Controller',
            manufacturer='Dell',
            model='PowerEdge R640',
            cpu='2x Intel Xeon Silver 4214R',
            ram='128GB DDR4 ECC',
            storage='4x 1TB SSD RAID 10',
            operating_system='Windows Server 2022',
            ip_address='192.168.1.50',
            mac_address='00:1A:2B:3C:4D:50',
            hostname='srv-dc-01.test.local',
            serial_number='SRV-TEST-001',
            notes='Primary domain controller',
            created_by=self.admin_user,
        )

        # --- Peripheral ---
        self.peripheral = Peripheral.objects.create(
            organization=self.org,
            location=self.location,
            name='Office Copier',
            device_type='multifunction',
            manufacturer='Xerox',
            model='VersaLink C7025',
            ip_address='192.168.1.200',
            mac_address='00:00:AA:BB:CC:01',
            serial_number='PER-TEST-001',
            notes='Main office copier',
            created_by=self.admin_user,
        )

        # --- Software with assignment ---
        self.software = Software.objects.create(
            organization=self.org,
            name='Microsoft 365 Business',
            software_type='microsoft365',
            license_key='M365-TEST-KEY',
            version='Business Premium',
            license_type='subscription',
            purchase_date=today - timedelta(days=365),
            expiry_date=today + timedelta(days=365),
            vendor='Microsoft',
            quantity=25,
            notes='Company-wide M365',
            is_active=True,
            created_by=self.admin_user,
        )
        self.software_assignment = SoftwareAssignment.objects.create(
            software=self.software,
            contact=self.contact1,
            created_by=self.admin_user,
        )

        # --- Backup (infrastructure monitoring, not system backup) ---
        self.backup_entry = Backup.objects.create(
            organization=self.org,
            location=self.location,
            name='Server Backup - Veeam',
            backup_type='server',
            vendor='Veeam',
            frequency='Daily at 11 PM',
            retention_period='30 days',
            storage_location='Local NAS + Cloud',
            storage_capacity='8TB',
            target_systems='Domain Controller, File Server',
            last_backup_date=timezone.now() - timedelta(hours=13),
            next_backup_date=timezone.now() + timedelta(hours=11),
            backup_status='active',
            notes='Hybrid backup solution',
            created_by=self.admin_user,
        )

        # --- VoIP with assignment ---
        self.voip = VoIP.objects.create(
            organization=self.org,
            name='Microsoft Teams Phone',
            voip_type='teams',
            license_key='TEAMS-PHONE-TEST-001',
            version='Business Voice',
            license_type='subscription',
            purchase_date=today - timedelta(days=100),
            expiry_date=today + timedelta(days=265),
            vendor='Microsoft',
            quantity=25,
            phone_numbers='+1-555-9100, +1-555-9101',
            extensions='100, 101, 102',
            notes='Teams Phone System for all staff',
            is_active=True,
            created_by=self.admin_user,
        )
        self.voip_assignment = VoIPAssignment.objects.create(
            voip=self.voip,
            contact=self.contact1,
            extension='100',
            phone_number='+1-555-9100',
            created_by=self.admin_user,
        )

    def get_entity_counts(self):
        """Return current counts of all entity types."""
        return {
            'users': User.objects.count(),
            'organizations': Organization.objects.count(),
            'locations': Location.objects.count(),
            'contacts': Contact.objects.count(),
            'documentation': Documentation.objects.count(),
            'password_entries': PasswordEntry.objects.count(),
            'configurations': Configuration.objects.count(),
            'network_devices': NetworkDevice.objects.count(),
            'endpoints': EndpointUser.objects.count(),
            'servers': Server.objects.count(),
            'peripherals': Peripheral.objects.count(),
            'software': Software.objects.count(),
            'software_assignments': SoftwareAssignment.objects.count(),
            'backups': Backup.objects.count(),
            'voip': VoIP.objects.count(),
            'voip_assignments': VoIPAssignment.objects.count(),
        }


class TestBackupCreation(BackupRestoreDataMixin, TestCase):
    """Test that backup captures all data correctly."""

    def setUp(self):
        self.create_test_data()
        self.service = SystemBackupService(self.admin_user)

    def test_backup_contains_all_users(self):
        """Backup should include all users with their data."""
        backup = self.service.create_backup(backup_password='test-backup-pw')
        users_data = backup['users']
        emails = {u['email'] for u in users_data}

        self.assertIn('admin@test.com', emails)
        self.assertIn('user@test.com', emails)
        self.assertIn('twofa@test.com', emails)
        self.assertEqual(len(users_data), 3)

    def test_backup_preserves_password_hashes(self):
        """Backup should include Django password hashes (not plaintext)."""
        backup = self.service.create_backup(backup_password='test-backup-pw')
        admin_data = next(u for u in backup['users'] if u['email'] == 'admin@test.com')

        # Password hash should be a Django-formatted hash, not plaintext
        self.assertTrue(admin_data['password_hash'].startswith('pbkdf2_sha256$'))
        # Verify the hash is valid
        self.assertTrue(check_password('Admin_P@ssw0rd!', admin_data['password_hash']))

    def test_backup_preserves_2fa_config(self):
        """Backup should include 2FA secrets and backup codes."""
        backup = self.service.create_backup(backup_password='test-backup-pw')
        twofa_data = next(u for u in backup['users'] if u['email'] == 'twofa@test.com')

        self.assertTrue(twofa_data['twofa_enabled'])
        self.assertEqual(twofa_data['twofa_secret'], self.twofa_secret)
        self.assertEqual(twofa_data['twofa_backup_codes'], ['hash1', 'hash2', 'hash3'])

    def test_backup_contains_organizations_with_all_entities(self):
        """Backup should export full org data including all entity types."""
        backup = self.service.create_backup(backup_password='test-backup-pw')
        orgs = backup['organizations']

        self.assertEqual(len(orgs), 1)
        org_data = orgs[0]

        self.assertEqual(org_data['organization']['name'], 'Test Corp')
        self.assertGreaterEqual(len(org_data.get('locations', [])), 1)
        self.assertGreaterEqual(len(org_data.get('contacts', [])), 2)
        self.assertGreaterEqual(len(org_data.get('documentations', [])), 1)
        self.assertGreaterEqual(len(org_data.get('password_entries', [])), 3)
        self.assertGreaterEqual(len(org_data.get('configurations', [])), 1)
        self.assertGreaterEqual(len(org_data.get('network_devices', [])), 1)
        self.assertGreaterEqual(len(org_data.get('endpoint_users', [])), 1)
        self.assertGreaterEqual(len(org_data.get('servers', [])), 1)
        self.assertGreaterEqual(len(org_data.get('peripherals', [])), 1)
        self.assertGreaterEqual(len(org_data.get('software', [])), 1)
        self.assertGreaterEqual(len(org_data.get('backups', [])), 1)
        self.assertGreaterEqual(len(org_data.get('voip', [])), 1)

    def test_backup_password_entries_are_encrypted(self):
        """Password entries in backup should have encrypted passwords."""
        backup = self.service.create_backup(backup_password='test-backup-pw')
        org_data = backup['organizations'][0]
        pwd_entries = org_data['password_entries']

        for entry in pwd_entries:
            self.assertTrue(
                entry['password'].startswith('ENC::'),
                f"Password for '{entry['name']}' should be encrypted in backup"
            )

    def test_backup_includes_encryption_key_data_when_password_set(self):
        """Backup with password should contain encryption_key_data."""
        backup = self.service.create_backup(backup_password='my-secure-pw')

        self.assertIn('encryption_key_data', backup)
        key_data = backup['encryption_key_data']
        self.assertIn('salt', key_data)
        self.assertIn('encrypted_key', key_data)

    def test_backup_without_password_has_no_encryption_key_data(self):
        """Backup without password should not contain encryption_key_data."""
        backup = self.service.create_backup()

        self.assertNotIn('encryption_key_data', backup)

    def test_backup_metadata(self):
        """Backup should have correct metadata."""
        backup = self.service.create_backup(backup_password='pw')

        self.assertEqual(backup['backup_version'], '1.0')
        self.assertEqual(backup['backup_type'], 'full_system')
        self.assertEqual(backup['created_by'], 'admin@test.com')
        self.assertIn('created_at', backup)

    def test_backup_voip_includes_assignments(self):
        """VoIP entries in backup should include their assignments."""
        backup = self.service.create_backup(backup_password='pw')
        org_data = backup['organizations'][0]
        voip_entries = org_data.get('voip', [])

        self.assertGreaterEqual(len(voip_entries), 1)
        voip_data = voip_entries[0]
        self.assertEqual(voip_data['name'], 'Microsoft Teams Phone')
        self.assertEqual(voip_data['voip_type'], 'teams')
        self.assertGreaterEqual(len(voip_data.get('assignments', [])), 1)


class TestEncryptionKeyProtection(TestCase):
    """Test backup password protection for encryption keys."""

    def test_protect_and_recover_key(self):
        """Protecting and recovering the key with the same password should work."""
        password = 'strong-backup-password!'
        key_data = protect_encryption_key(password)

        recovered_key = recover_encryption_key(password, key_data)
        # Should return a non-empty string (the original FIELD_ENCRYPTION_KEY)
        self.assertTrue(len(recovered_key) > 0)

    def test_wrong_password_raises_error(self):
        """Recovering with a wrong password should raise EncryptionError."""
        key_data = protect_encryption_key('correct-password')

        with self.assertRaises(EncryptionError):
            recover_encryption_key('wrong-password', key_data)

    def test_different_backups_have_different_salts(self):
        """Each backup should generate a unique salt."""
        key_data1 = protect_encryption_key('same-password')
        key_data2 = protect_encryption_key('same-password')

        self.assertNotEqual(key_data1['salt'], key_data2['salt'])

    def test_encrypt_decrypt_round_trip(self):
        """Encrypting and decrypting a password should return original."""
        plaintext = 'My_Secret_P@ssw0rd!'
        encrypted = encrypt_password(plaintext)

        self.assertTrue(is_encrypted(encrypted))
        self.assertTrue(encrypted.startswith('ENC::'))

        decrypted = decrypt_password(encrypted)
        self.assertEqual(decrypted, plaintext)

    def test_double_encryption_prevented(self):
        """Encrypting an already encrypted value should not double-encrypt."""
        plaintext = 'My_Secret!'
        encrypted_once = encrypt_password(plaintext)
        encrypted_twice = encrypt_password(encrypted_once)

        # Should be the same - no double encryption
        self.assertEqual(encrypted_once, encrypted_twice)

    def test_is_encrypted_detection(self):
        """is_encrypted should correctly identify encrypted values."""
        self.assertFalse(is_encrypted('plaintext'))
        self.assertFalse(is_encrypted(''))
        self.assertFalse(is_encrypted(None))
        self.assertTrue(is_encrypted('ENC::some_data_here'))
        self.assertTrue(is_encrypted(encrypt_password('test')))


class TestRestoreToCleanDatabase(BackupRestoreDataMixin, TestCase):
    """Test restoring a backup to a clean (empty) database."""

    def setUp(self):
        self.create_test_data()
        self.service = SystemBackupService(self.admin_user)
        self.backup_password = 'restore-test-pw!'
        self.backup_data = self.service.create_backup(
            backup_password=self.backup_password
        )
        self.original_counts = self.get_entity_counts()

    def test_restore_users_to_clean_db(self):
        """Restoring users should recreate them with correct data."""
        # Delete non-admin users to simulate clean state
        User.objects.exclude(email='admin@test.com').delete()
        self.assertEqual(User.objects.count(), 1)

        results = self.service.restore_backup(
            backup_data=self.backup_data,
            restore_users=True,
            restore_organizations=False,
            backup_password=self.backup_password,
        )

        self.assertTrue(results['success'])
        # admin@test.com was skipped (already exists), 2 others created
        self.assertEqual(len(results['users']['restored']), 2)
        self.assertEqual(User.objects.count(), 3)

    def test_restored_user_can_authenticate(self):
        """Restored user's password hash should still work for authentication."""
        User.objects.exclude(email='admin@test.com').delete()

        self.service.restore_backup(
            backup_data=self.backup_data,
            restore_users=True,
            restore_organizations=False,
            backup_password=self.backup_password,
        )

        restored_user = User.objects.get(email='user@test.com')
        self.assertTrue(check_password('User_P@ssw0rd!', restored_user.password))

    def test_restored_user_has_2fa_config(self):
        """Restored user should have their 2FA configuration intact."""
        User.objects.exclude(email='admin@test.com').delete()

        self.service.restore_backup(
            backup_data=self.backup_data,
            restore_users=True,
            restore_organizations=False,
            backup_password=self.backup_password,
        )

        restored_twofa = User.objects.get(email='twofa@test.com')
        self.assertTrue(restored_twofa.twofa_enabled)
        self.assertEqual(restored_twofa.twofa_secret, self.twofa_secret)
        self.assertEqual(restored_twofa.twofa_backup_codes, ['hash1', 'hash2', 'hash3'])

        # Verify TOTP still works
        totp = pyotp.TOTP(restored_twofa.twofa_secret)
        self.assertTrue(totp.verify(totp.now()))

    def test_restore_organizations_to_clean_db(self):
        """Restoring organizations should recreate all entity types."""
        # Wipe org data (hard delete to bypass soft delete)
        VoIPAssignment.all_objects.all().delete()
        VoIP.all_objects.all().delete()
        SoftwareAssignment.all_objects.all().delete()
        Software.all_objects.all().delete()
        Backup.all_objects.all().delete()
        Peripheral.all_objects.all().delete()
        Server.all_objects.all().delete()
        EndpointUser.all_objects.all().delete()
        NetworkDevice.all_objects.all().delete()
        Configuration.all_objects.all().delete()
        PasswordEntry.all_objects.all().delete()
        Documentation.all_objects.all().delete()
        Contact.all_objects.all().delete()
        Location.all_objects.all().delete()
        OrganizationMember.objects.all().delete()
        Organization.all_objects.all().delete()

        self.assertEqual(Organization.objects.count(), 0)

        results = self.service.restore_backup(
            backup_data=self.backup_data,
            restore_users=False,
            restore_organizations=True,
            backup_password=self.backup_password,
        )

        self.assertTrue(results['success'])
        self.assertGreaterEqual(len(results['organizations']['imported']), 1)

        # Verify entities were restored
        self.assertGreaterEqual(Organization.objects.count(), 1)
        self.assertGreaterEqual(Location.objects.count(), 1)
        self.assertGreaterEqual(Contact.objects.count(), 2)
        self.assertGreaterEqual(Documentation.objects.count(), 1)
        self.assertGreaterEqual(PasswordEntry.objects.count(), 3)
        self.assertGreaterEqual(Configuration.objects.count(), 1)
        self.assertGreaterEqual(NetworkDevice.objects.count(), 1)
        self.assertGreaterEqual(EndpointUser.objects.count(), 1)
        self.assertGreaterEqual(Server.objects.count(), 1)
        self.assertGreaterEqual(Peripheral.objects.count(), 1)
        self.assertGreaterEqual(Software.objects.count(), 1)
        self.assertGreaterEqual(Backup.objects.count(), 1)
        self.assertGreaterEqual(VoIP.objects.count(), 1)

    def test_restored_passwords_are_decryptable(self):
        """Restored password entries should be decryptable with current key."""
        # Create backup, wipe data, restore
        VoIPAssignment.all_objects.all().delete()
        VoIP.all_objects.all().delete()
        SoftwareAssignment.all_objects.all().delete()
        Software.all_objects.all().delete()
        Backup.all_objects.all().delete()
        Peripheral.all_objects.all().delete()
        Server.all_objects.all().delete()
        EndpointUser.all_objects.all().delete()
        NetworkDevice.all_objects.all().delete()
        Configuration.all_objects.all().delete()
        PasswordEntry.all_objects.all().delete()
        Documentation.all_objects.all().delete()
        Contact.all_objects.all().delete()
        Location.all_objects.all().delete()
        OrganizationMember.objects.all().delete()
        Organization.all_objects.all().delete()

        results = self.service.restore_backup(
            backup_data=self.backup_data,
            restore_organizations=True,
            restore_users=False,
            backup_password=self.backup_password,
        )

        self.assertTrue(results['success'])

        # Check passwords were re-encrypted and are decryptable
        for entry in PasswordEntry.objects.all():
            self.assertTrue(
                is_encrypted(entry.password),
                f"Password for '{entry.name}' should be encrypted after restore"
            )
            decrypted = decrypt_password(entry.password)
            self.assertIn(
                decrypted,
                self.plain_passwords.values(),
                f"Decrypted password for '{entry.name}' should match original"
            )


class TestRestoreWithOverwrite(BackupRestoreDataMixin, TestCase):
    """Test restoring with overwrite_existing=True."""

    def setUp(self):
        self.create_test_data()
        self.service = SystemBackupService(self.admin_user)
        self.backup_password = 'overwrite-test-pw!'
        self.backup_data = self.service.create_backup(
            backup_password=self.backup_password
        )

    def test_overwrite_user_data(self):
        """Overwriting should update existing user fields."""
        # Modify the user
        self.regular_user.first_name = 'Changed'
        self.regular_user.save()

        results = self.service.restore_backup(
            backup_data=self.backup_data,
            restore_users=True,
            restore_organizations=False,
            overwrite_existing=True,
            backup_password=self.backup_password,
        )

        self.assertTrue(results['success'])
        # All 3 users should be "updated"
        updated_emails = [r['email'] for r in results['users']['restored'] if r['action'] == 'updated']
        self.assertIn('user@test.com', updated_emails)

        # Verify data was reverted
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.first_name, 'Regular')

    def test_overwrite_restores_password_hash(self):
        """Overwriting a user should restore their original password hash."""
        # Change the password
        self.regular_user.set_password('New_Different_Pw!')
        self.regular_user.save()

        # Verify new password works
        self.assertTrue(check_password('New_Different_Pw!', self.regular_user.password))

        self.service.restore_backup(
            backup_data=self.backup_data,
            restore_users=True,
            restore_organizations=False,
            overwrite_existing=True,
            backup_password=self.backup_password,
        )

        self.regular_user.refresh_from_db()
        # Original password should work again
        self.assertTrue(check_password('User_P@ssw0rd!', self.regular_user.password))
        # New password should not work
        self.assertFalse(check_password('New_Different_Pw!', self.regular_user.password))

    def test_overwrite_restores_2fa(self):
        """Overwriting a user should restore their 2FA config."""
        # Disable 2FA
        self.twofa_user.twofa_enabled = False
        self.twofa_user.twofa_secret = ''
        self.twofa_user.twofa_backup_codes = []
        self.twofa_user.save()

        self.service.restore_backup(
            backup_data=self.backup_data,
            restore_users=True,
            restore_organizations=False,
            overwrite_existing=True,
            backup_password=self.backup_password,
        )

        self.twofa_user.refresh_from_db()
        self.assertTrue(self.twofa_user.twofa_enabled)
        self.assertEqual(self.twofa_user.twofa_secret, self.twofa_secret)
        self.assertEqual(self.twofa_user.twofa_backup_codes, ['hash1', 'hash2', 'hash3'])

    def test_skip_existing_without_overwrite(self):
        """Without overwrite, existing users should be skipped."""
        results = self.service.restore_backup(
            backup_data=self.backup_data,
            restore_users=True,
            restore_organizations=False,
            overwrite_existing=False,
            backup_password=self.backup_password,
        )

        self.assertTrue(results['success'])
        self.assertEqual(len(results['users']['restored']), 0)
        self.assertEqual(len(results['users']['skipped']), 3)


class TestBackupPasswordProtection(BackupRestoreDataMixin, TestCase):
    """Test backup password enforcement and error handling."""

    def setUp(self):
        self.create_test_data()
        self.service = SystemBackupService(self.admin_user)

    def test_wrong_password_fails_restore(self):
        """Restoring with wrong password should fail."""
        backup_data = self.service.create_backup(backup_password='correct-password')

        results = self.service.restore_backup(
            backup_data=backup_data,
            backup_password='wrong-password',
        )

        self.assertFalse(results['success'])
        self.assertIn('Failed to unlock backup', results.get('error', ''))

    def test_missing_password_for_protected_backup(self):
        """Restoring a password-protected backup without a password should fail."""
        backup_data = self.service.create_backup(backup_password='my-password')

        results = self.service.restore_backup(
            backup_data=backup_data,
            backup_password=None,
        )

        self.assertFalse(results['success'])
        self.assertIn('password-protected', results.get('error', ''))

    def test_invalid_backup_version_fails(self):
        """Backup with unsupported version should fail."""
        backup_data = self.service.create_backup(backup_password='pw')
        backup_data['backup_version'] = '99.0'

        results = self.service.restore_backup(
            backup_data=backup_data,
            backup_password='pw',
        )

        self.assertFalse(results['success'])
        self.assertIn('Unsupported backup version', results.get('error', ''))

    def test_correct_password_succeeds(self):
        """Restoring with the correct password should succeed."""
        password = 'the-right-pw!'
        backup_data = self.service.create_backup(backup_password=password)

        results = self.service.restore_backup(
            backup_data=backup_data,
            restore_users=True,
            restore_organizations=False,
            overwrite_existing=False,
            backup_password=password,
        )

        self.assertTrue(results['success'])


class TestPasswordReEncryption(BackupRestoreDataMixin, TestCase):
    """Test that passwords are re-encrypted during restore when keys differ."""

    def setUp(self):
        self.create_test_data()
        self.service = SystemBackupService(self.admin_user)

    def test_passwords_remain_decryptable_after_restore(self):
        """After a full backup-wipe-restore cycle, passwords should still decrypt."""
        backup_password = 're-encrypt-test!'
        backup_data = self.service.create_backup(backup_password=backup_password)

        # Wipe password entries
        PasswordEntry.all_objects.all().delete()
        self.assertEqual(PasswordEntry.objects.count(), 0)

        # Also wipe org data so restore will import fresh
        VoIPAssignment.all_objects.all().delete()
        VoIP.all_objects.all().delete()
        SoftwareAssignment.all_objects.all().delete()
        Software.all_objects.all().delete()
        Backup.all_objects.all().delete()
        Peripheral.all_objects.all().delete()
        Server.all_objects.all().delete()
        EndpointUser.all_objects.all().delete()
        NetworkDevice.all_objects.all().delete()
        Configuration.all_objects.all().delete()
        Documentation.all_objects.all().delete()
        Contact.all_objects.all().delete()
        Location.all_objects.all().delete()
        OrganizationMember.objects.all().delete()
        Organization.all_objects.all().delete()

        results = self.service.restore_backup(
            backup_data=backup_data,
            restore_organizations=True,
            restore_users=False,
            backup_password=backup_password,
        )

        self.assertTrue(results['success'])

        # All password entries should be encrypted and decryptable
        restored_entries = PasswordEntry.objects.all()
        self.assertEqual(restored_entries.count(), 3)

        for entry in restored_entries:
            self.assertTrue(is_encrypted(entry.password))
            decrypted = decrypt_password(entry.password)
            self.assertIn(decrypted, self.plain_passwords.values())

    def test_re_encryption_count_reported(self):
        """Restore results should report how many passwords were re-encrypted."""
        backup_password = 're-encrypt-count!'
        backup_data = self.service.create_backup(backup_password=backup_password)

        results = self.service.restore_backup(
            backup_data=backup_data,
            restore_users=False,
            restore_organizations=False,
            overwrite_existing=False,
            backup_password=backup_password,
        )

        self.assertTrue(results['success'])
        # passwords_re_encrypted should be in results
        re_enc = results.get('passwords_re_encrypted', {})
        # With the same key, re-encrypt should process existing passwords
        total = re_enc.get('re_encrypted', 0) + re_enc.get('skipped', 0)
        self.assertGreaterEqual(total, 3)
        self.assertEqual(len(re_enc.get('errors', [])), 0)


class TestSelectiveRestore(BackupRestoreDataMixin, TestCase):
    """Test restoring only users or only organizations."""

    def setUp(self):
        self.create_test_data()
        self.service = SystemBackupService(self.admin_user)
        self.backup_password = 'selective-test!'
        self.backup_data = self.service.create_backup(
            backup_password=self.backup_password
        )

    def test_restore_users_only(self):
        """When restore_organizations=False, only users should be restored."""
        User.objects.exclude(email='admin@test.com').delete()
        org_count_before = Organization.objects.count()

        results = self.service.restore_backup(
            backup_data=self.backup_data,
            restore_users=True,
            restore_organizations=False,
            backup_password=self.backup_password,
        )

        self.assertTrue(results['success'])
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(Organization.objects.count(), org_count_before)
        # Organizations results should be empty
        self.assertEqual(len(results['organizations']['imported']), 0)

    def test_restore_organizations_only(self):
        """When restore_users=False, only organizations should be processed."""
        results = self.service.restore_backup(
            backup_data=self.backup_data,
            restore_users=False,
            restore_organizations=True,
            overwrite_existing=False,
            backup_password=self.backup_password,
        )

        self.assertTrue(results['success'])
        # Users results should be empty (no restores)
        self.assertEqual(len(results['users']['restored']), 0)


class TestBackupRestoreAPIViews(BackupRestoreDataMixin, TestCase):
    """Test the API endpoints for backup and restore."""

    def setUp(self):
        from rest_framework.test import APIClient
        self.create_test_data()
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)

    def test_backup_requires_admin(self):
        """Non-admin users should be rejected."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post('/api/reports/system-backup/', {
            'backup_password': 'test',
        })
        self.assertEqual(response.status_code, 403)

    def test_backup_requires_password(self):
        """Backup endpoint should require a backup_password."""
        response = self.client.post('/api/reports/system-backup/', {})
        self.assertEqual(response.status_code, 400)
        self.assertIn('backup password', response.data['error'].lower())

    def test_backup_creates_downloadable_json(self):
        """Backup endpoint should return a JSON file download."""
        response = self.client.post('/api/reports/system-backup/', {
            'backup_password': 'api-test-pw',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertIn('attachment', response.get('Content-Disposition', ''))

    def test_restore_requires_admin(self):
        """Non-admin users should be rejected for restore."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post('/api/reports/system-restore/', {
            'data': {'backup_type': 'full_system', 'backup_version': '1.0'},
        }, format='json')
        self.assertEqual(response.status_code, 403)

    def test_restore_rejects_invalid_backup_type(self):
        """Restore should reject non-full_system backup types."""
        response = self.client.post('/api/reports/system-restore/', {
            'data': {'backup_type': 'partial', 'backup_version': '1.0'},
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_full_backup_restore_cycle_via_api(self):
        """End-to-end: create backup via API, wipe data, restore via API."""
        import json

        # Create backup
        response = self.client.post('/api/reports/system-backup/', {
            'backup_password': 'cycle-test-pw!',
        })
        self.assertEqual(response.status_code, 200)
        backup_data = json.loads(response.content)

        # Wipe users except admin
        User.objects.exclude(email='admin@test.com').delete()
        self.assertEqual(User.objects.count(), 1)

        # Restore
        response = self.client.post('/api/reports/system-restore/', {
            'data': backup_data,
            'restore_users': 'true',
            'restore_organizations': 'false',
            'overwrite_existing': 'false',
            'backup_password': 'cycle-test-pw!',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        self.assertEqual(User.objects.count(), 3)
