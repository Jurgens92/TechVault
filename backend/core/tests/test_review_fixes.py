"""
Regression tests for the issues found in the code review:
privilege escalation, backup codes, audit logging, soft-delete integrity,
token revocation, import permissions, assignment handling and validation.
"""
import io
import json

import pyotp
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from core.models import (
    AuditLog, Contact, InternetConnection, Location, NetworkDevice, Organization,
    PasswordEntry, Server, Software, VoIP, VoIPAssignment,
)

User = get_user_model()
PASSWORD = 'Str0ng!Passw0rd#1'


def make_user(email, staff=False, superuser=False):
    user = User.objects.create_user(
        email=email, password=PASSWORD, first_name='Test', last_name='User',
        is_staff=staff, is_superuser=superuser,
    )
    user.twofa_enabled = True
    user.twofa_secret = pyotp.random_base32()
    user.save()
    return user


class ReviewFixesBase(TestCase):
    def setUp(self):
        cache.clear()  # reset throttle counters between tests
        self.admin = make_user('admin@example.com', staff=True, superuser=True)
        self.user = make_user('user@example.com')
        self.other = make_user('other@example.com')
        self.admin_client = self.client_for(self.admin)
        self.client_ = self.client_for(self.user)
        self.other_client = self.client_for(self.other)
        self.org = Organization.objects.create(name='Acme', created_by=self.user)

    def client_for(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    def login(self, user, token=None):
        cache.clear()
        return APIClient().post('/api/auth/login/', {
            'email': user.email, 'password': PASSWORD,
            'twofa_token': token or pyotp.TOTP(user.twofa_secret).now(),
        }, format='json')


class PrivilegeEscalationTests(ReviewFixesBase):
    def test_user_cannot_make_themselves_admin_via_profile(self):
        response = self.client_.patch('/api/user/profile/', {'is_staff': True, 'is_active': False}, format='json')
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff)
        self.assertTrue(self.user.is_active)
        self.assertEqual(self.client_.get('/api/users/').status_code, 403)

    def test_user_cannot_make_themselves_admin_via_auth_user(self):
        self.client_.patch('/api/auth/user/', {'is_staff': True}, format='json')
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff)

    def test_admin_can_still_change_roles(self):
        response = self.admin_client.patch(f'/api/users/{self.user.id}/', {'is_staff': True}, format='json')
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_staff)

    def test_last_admin_cannot_be_demoted_or_self_demote(self):
        response = self.admin_client.patch(f'/api/users/{self.admin.id}/', {'is_staff': False}, format='json')
        self.assertEqual(response.status_code, 400)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_staff)

    def test_weak_password_on_user_create_is_a_validation_error(self):
        response = self.admin_client.post('/api/users/', {
            'email': 'new@example.com', 'first_name': 'N', 'last_name': 'U', 'password': 'password',
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)

    def test_admin_recovery_actions(self):
        self.user.failed_login_attempts = 5
        self.user.record_failed_login()
        self.assertTrue(self.user.is_locked())

        self.assertEqual(self.admin_client.post(f'/api/users/{self.user.id}/unlock/').status_code, 200)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_locked())

        self.assertEqual(self.admin_client.post(f'/api/users/{self.user.id}/reset-2fa/').status_code, 200)
        self.user.refresh_from_db()
        self.assertFalse(self.user.twofa_enabled)
        self.assertIsNone(self.user.twofa_secret)

        weak = self.admin_client.post(f'/api/users/{self.user.id}/reset-password/', {'password': '123'}, format='json')
        self.assertEqual(weak.status_code, 400)
        ok = self.admin_client.post(
            f'/api/users/{self.user.id}/reset-password/', {'password': 'An0ther!Str0ngOne'}, format='json'
        )
        self.assertEqual(ok.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('An0ther!Str0ngOne'))

        # Non-admins cannot use them
        self.assertEqual(self.other_client.post(f'/api/users/{self.user.id}/reset-2fa/').status_code, 403)


class TwoFactorTests(ReviewFixesBase):
    def _new_codes(self, user):
        response = self.client_for(user).post(
            '/api/auth/2fa/backup-codes/regenerate/', {'password': PASSWORD}, format='json'
        )
        return response.data['backup_codes']

    def test_backup_code_logs_in_exactly_as_displayed(self):
        codes = self._new_codes(self.user)
        response = self.login(self.user, token=codes[0])
        self.assertEqual(response.status_code, 200, response.data)
        self.assertTrue(response.data['backup_code_used'])
        self.assertEqual(response.data['remaining_backup_codes'], 9)
        # ...and only once
        self.assertEqual(self.login(self.user, token=codes[0]).status_code, 401)

    def test_backup_code_accepts_no_dashes_and_lowercase(self):
        codes = self._new_codes(self.user)
        response = self.login(self.user, token=codes[1].replace('-', '').lower())
        self.assertEqual(response.status_code, 200)

    def test_backup_codes_issued_before_the_fix_still_work(self):
        import hashlib
        self.user.twofa_backup_codes = [hashlib.sha256(b'AB12-CD34-EF56').hexdigest()]
        self.user.save()
        self.assertEqual(self.login(self.user, token='AB12-CD34-EF56').status_code, 200)

    def test_setup_cannot_replace_secret_of_enabled_account(self):
        secret = self.user.twofa_secret
        response = self.client_.post('/api/auth/2fa/setup/')
        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertEqual(self.user.twofa_secret, secret)


class TokenAndCookieTests(ReviewFixesBase):
    def test_login_sets_httponly_cookies_and_cookie_auth_works(self):
        client = APIClient()
        cache.clear()
        response = client.post('/api/auth/login/', {
            'email': self.user.email, 'password': PASSWORD,
            'twofa_token': pyotp.TOTP(self.user.twofa_secret).now(),
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.cookies['techvault-auth']['httponly'])
        self.assertTrue(response.cookies['techvault-refresh-token']['httponly'])
        # The client now carries the cookies; no Authorization header needed
        self.assertEqual(client.get('/api/user/profile/').status_code, 200)

    def test_cookie_authenticated_writes_require_csrf(self):
        login = self.login(self.user)
        client = APIClient(enforce_csrf_checks=True)
        client.cookies['techvault-auth'] = login.data['access_token']
        response = client.post('/api/organizations/', {'name': 'CSRF Org'}, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Organization.objects.filter(name='CSRF Org').exists())

    def test_rotated_refresh_token_cannot_be_reused(self):
        refresh = self.login(self.user).data['refresh_token']
        client = APIClient()
        self.assertEqual(client.post('/api/token/refresh/', {'refresh': refresh}, format='json').status_code, 200)
        self.assertEqual(client.post('/api/token/refresh/', {'refresh': refresh}, format='json').status_code, 401)

    def test_logout_revokes_refresh_token(self):
        refresh = self.login(self.user).data['refresh_token']
        client = APIClient()
        self.assertEqual(client.post('/api/auth/logout/', {'refresh': refresh}, format='json').status_code, 200)
        self.assertEqual(client.post('/api/token/refresh/', {'refresh': refresh}, format='json').status_code, 401)

    def test_2fa_enforced_for_cookie_auth(self):
        self.user.twofa_enabled = False
        self.user.save()
        cache.clear()
        client = APIClient()
        client.post('/api/auth/login/', {'email': self.user.email, 'password': PASSWORD}, format='json')
        self.assertEqual(client.get('/api/organizations/').status_code, 403)


class AuditLogTests(ReviewFixesBase):
    def test_create_update_delete_restore_are_logged(self):
        response = self.client_.post('/api/contacts/', {
            'organization': str(self.org.id), 'first_name': 'J', 'last_name': 'D', 'email': 'j@d.com',
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        cid = response.data['id']
        self.client_.patch(f'/api/contacts/{cid}/', {'title': 'CTO'}, format='json')
        self.client_.delete(f'/api/contacts/{cid}/')
        self.client_.post(f'/api/contacts/{cid}/restore/')
        actions = list(
            AuditLog.objects.filter(entity_type='Contact').order_by('timestamp').values_list('action', flat=True)
        )
        self.assertEqual(actions, ['create', 'update', 'delete', 'restore'])

    def test_organization_create_is_logged_and_sets_created_by(self):
        response = self.client_.post('/api/organizations/', {'name': 'NewCo'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(AuditLog.objects.filter(action='create', entity_type='Organization').exists())
        self.assertEqual(Organization.objects.get(name='NewCo').created_by, self.user)

    def test_password_reveal_is_logged_without_the_secret(self):
        response = self.client_.post('/api/passwords/', {
            'organization': str(self.org.id), 'name': 'router', 'password': 'hunter2-secret',
        }, format='json')
        pid = response.data['id']
        reveal = self.client_.post(f'/api/passwords/{pid}/retrieve_password/')
        self.assertEqual(reveal.data['password'], 'hunter2-secret')
        self.assertTrue(AuditLog.objects.filter(action='view', entity_type='PasswordEntry', entity_id=pid).exists())
        dump = json.dumps(list(AuditLog.objects.values('changes', 'details')), default=str)
        self.assertNotIn('hunter2-secret', dump)

    def test_audit_log_list_is_admin_only_and_loads(self):
        self.client_.post('/api/organizations/', {'name': 'Logged'}, format='json')
        response = self.admin_client.get('/api/audit-logs/')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data['count'], 1)
        self.assertEqual(self.client_.get('/api/audit-logs/').status_code, 403)

    def test_every_list_endpoint_loads(self):
        """Smoke test: each collection (and its deleted view) answers 200."""
        for name in (
            'organizations', 'locations', 'contacts', 'documentations', 'passwords',
            'configurations', 'network-devices', 'endpoint-users', 'servers',
            'peripherals', 'software', 'backups', 'voip',
        ):
            self.assertEqual(self.client_.get(f'/api/{name}/').status_code, 200, name)
            self.assertEqual(self.client_.get(f'/api/{name}/deleted/').status_code, 200, name)
        self.assertEqual(self.admin_client.get('/api/users/').status_code, 200)

    def test_login_is_logged(self):
        self.login(self.user)
        self.assertTrue(AuditLog.objects.filter(action='login', user=self.user).exists())


class SoftDeleteIntegrityTests(ReviewFixesBase):
    def test_name_can_be_reused_after_delete(self):
        first = self.client_.post('/api/organizations/', {'name': 'Dup'}, format='json')
        self.client_.delete(f"/api/organizations/{first.data['id']}/")
        second = self.client_.post('/api/organizations/', {'name': 'Dup'}, format='json')
        self.assertEqual(second.status_code, 201, second.data)

        data = {'organization': str(self.org.id), 'first_name': 'J', 'last_name': 'D', 'email': 'j@d.com'}
        contact = self.client_.post('/api/contacts/', data, format='json')
        self.client_.delete(f"/api/contacts/{contact.data['id']}/")
        self.assertEqual(self.client_.post('/api/contacts/', data, format='json').status_code, 201)

    def test_duplicate_live_name_is_a_validation_error(self):
        response = self.client_.post('/api/organizations/', {'name': 'Acme'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('name', response.data)

    def test_restore_conflicting_with_live_record_is_rejected_cleanly(self):
        first = self.client_.post('/api/organizations/', {'name': 'Dup'}, format='json')
        self.client_.delete(f"/api/organizations/{first.data['id']}/")
        self.client_.post('/api/organizations/', {'name': 'Dup'}, format='json')
        response = self.client_.post(f"/api/organizations/{first.data['id']}/restore/")
        self.assertEqual(response.status_code, 400)

    def test_deleting_organization_hides_and_restores_its_children(self):
        kept_deleted = PasswordEntry.objects.create(organization=self.org, name='old', password='x')
        kept_deleted.delete()
        PasswordEntry.objects.create(organization=self.org, name='live', password='x')
        Server.objects.create(organization=self.org, name='srv')

        self.client_.delete(f'/api/organizations/{self.org.id}/')
        self.assertEqual(self.client_.get('/api/passwords/').data['count'], 0)
        self.assertEqual(self.client_.get('/api/servers/').data['count'], 0)
        self.assertEqual(self.client_.get('/api/dashboard/stats/').data['passwords'], 0)
        # Children are not listed individually while their organization is deleted
        self.assertEqual(self.client_.get('/api/servers/deleted/').data['count'], 0)
        server = Server.all_objects.get(name='srv')
        self.assertEqual(self.client_.post(f'/api/servers/{server.id}/restore/').status_code, 400)

        self.client_.post(f'/api/organizations/{self.org.id}/restore/')
        self.assertEqual(self.client_.get('/api/servers/').data['count'], 1)
        names = [p['name'] for p in self.client_.get('/api/passwords/').data['results']]
        # The entry that was already deleted before the organization stays deleted
        self.assertEqual(names, ['live'])

    def test_any_user_can_restore_in_shared_workspace(self):
        contact = Contact.objects.create(organization=self.org, first_name='a', last_name='b', email='a@b.com')
        self.client_.delete(f'/api/contacts/{contact.id}/')
        self.assertEqual(self.other_client.post(f'/api/contacts/{contact.id}/restore/').status_code, 200)

    def test_hard_delete_is_admin_only_and_logged(self):
        contact = Contact.objects.create(organization=self.org, first_name='a', last_name='b', email='a@b.com')
        self.assertEqual(self.client_.delete(f'/api/contacts/{contact.id}/hard_delete/').status_code, 403)
        self.assertEqual(self.admin_client.delete(f'/api/contacts/{contact.id}/hard_delete/').status_code, 204)
        self.assertFalse(Contact.all_objects.filter(pk=contact.id).exists())
        self.assertTrue(AuditLog.objects.filter(action='delete', details='Permanently deleted').exists())


class ImportPermissionTests(ReviewFixesBase):
    def _payload(self):
        return {
            'data': {'export_version': '1.0', 'organizations': [{'organization': {'id': str(self.org.id), 'name': 'Acme'}}]},
            'overwrite_existing': True,
        }

    def test_non_admin_cannot_import_or_overwrite(self):
        Server.objects.create(organization=self.org, name='srv')
        response = self.client_.post('/api/reports/import-organizations/', self._payload(), format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Server.objects.filter(organization=self.org).count(), 1)

    def test_admin_import_is_logged(self):
        response = self.admin_client.post('/api/reports/import-organizations/', self._payload(), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(AuditLog.objects.filter(action='import', entity_type='Organization').exists())

    def test_csv_import_validates_rows_and_is_open_to_all_users(self):
        csv_file = io.BytesIO(
            b'first_name,last_name,title,email,phone\n'
            b'Ann,Bee,CTO,ann@example.com,1\n'
            b',,,notanemail,\n'
            b'Ann,Dup,,ann@example.com,\n'
        )
        csv_file.name = 'contacts.csv'
        response = self.other_client.post(
            '/api/contacts/import_csv/', {'file': csv_file, 'organization_id': str(self.org.id)}, format='multipart'
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['created'], 1)
        self.assertEqual([e['row'] for e in response.data['errors']], [3, 4])
        self.assertEqual(Contact.objects.filter(organization=self.org).count(), 1)


class ExportRoundTripTests(ReviewFixesBase):
    def test_export_import_keeps_connections_hosts_history_and_deleted_state(self):
        from reports.export_import_service import OrganizationExportImportService

        device = NetworkDevice.objects.create(organization=self.org, name='fw')
        InternetConnection.objects.create(network_device=device, provider_name='ISP', download_speed=100, upload_speed=10)
        host = Server.objects.create(organization=self.org, name='host', raid_configuration='RAID 10')
        Server.objects.create(organization=self.org, name='vm', host_server=host)
        gone = Location.objects.create(
            organization=self.org, name='Old', address='a', city='c', postal_code='1', country='z'
        )
        gone.delete()
        created = self.client_.post('/api/passwords/', {
            'organization': str(self.org.id), 'name': 'pw', 'password': 'first',
        }, format='json')
        self.client_.patch(f"/api/passwords/{created.data['id']}/", {'password': 'second'}, format='json')

        service = OrganizationExportImportService(self.admin)
        exported = json.loads(json.dumps(service.export_organizations(include_deleted=True)))
        Organization.all_objects.filter(pk=self.org.pk).delete()

        result = service.import_organizations(exported)
        self.assertEqual(result['errors'], [])
        org = Organization.objects.get(name='Acme')
        self.assertEqual(InternetConnection.objects.filter(network_device__organization=org).count(), 1)
        vm = Server.objects.get(organization=org, name='vm')
        self.assertEqual(vm.host_server.name, 'host')
        self.assertEqual(vm.host_server.raid_configuration, 'RAID 10')
        self.assertFalse(Location.objects.filter(organization=org, name='Old').exists())
        self.assertTrue(Location.all_objects.filter(organization=org, name='Old').exists())
        entry = PasswordEntry.objects.get(organization=org, name='pw')
        self.assertEqual(entry.versions.count(), 2)

    def test_export_password_lets_another_server_read_vault_passwords(self):
        from django.test import override_settings
        from core import encryption
        from reports.export_import_service import OrganizationExportImportService

        created = self.client_.post('/api/passwords/', {
            'organization': str(self.org.id), 'name': 'pw', 'password': 'portable-secret',
        }, format='json')
        self.assertEqual(created.status_code, 201)
        service = OrganizationExportImportService(self.admin)
        exported = json.loads(json.dumps(service.export_organizations(export_password='exp-pw')))
        plain_export = json.loads(json.dumps(service.export_organizations()))
        Organization.all_objects.filter(pk=self.org.pk).delete()

        original = encryption.password_encryption
        try:
            with override_settings(FIELD_ENCRYPTION_KEY='a-completely-different-server-key'):
                encryption.password_encryption = encryption.PasswordEncryption()
                # Without the key the import warns instead of silently producing junk
                warned = service.import_organizations(plain_export)
                self.assertEqual(warned.get('undecryptable_passwords'), 1)
                Organization.all_objects.filter(name='Acme').delete()

                result = service.import_organizations(exported, export_password='exp-pw')
                self.assertNotIn('undecryptable_passwords', result)
                entry = PasswordEntry.objects.get(name='pw')
                self.assertEqual(encryption.decrypt_password(entry.password), 'portable-secret')
        finally:
            encryption.password_encryption = original


class AssignmentAndValidationTests(ReviewFixesBase):
    def setUp(self):
        super().setUp()
        self.c1 = Contact.objects.create(organization=self.org, first_name='a', last_name='a', email='a@x.com')
        self.c2 = Contact.objects.create(organization=self.org, first_name='b', last_name='b', email='b@x.com')
        self.foreign_org = Organization.objects.create(name='Other')
        self.foreign_contact = Contact.objects.create(
            organization=self.foreign_org, first_name='o', last_name='o', email='o@x.com'
        )

    def _voip(self, **extra):
        return self.client_.post('/api/voip/', {
            'organization': str(self.org.id), 'name': 'pbx', 'quantity': 2,
            'assigned_contact_ids': [str(self.c1.id), str(self.c2.id)], **extra,
        }, format='json')

    def test_resaving_keeps_assignment_details(self):
        vid = self._voip().data['id']
        VoIPAssignment.objects.filter(voip_id=vid, contact=self.c1).update(extension='101')
        response = self.client_.patch(f'/api/voip/{vid}/', {
            'notes': 'x', 'assigned_contact_ids': [str(self.c1.id)],
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([a['extension'] for a in response.data['assigned_contacts']], ['101'])
        self.assertEqual(response.data['assigned_count'], 1)

    def test_contacts_from_another_organization_are_rejected(self):
        response = self.client_.post('/api/voip/', {
            'organization': str(self.org.id), 'name': 'pbx', 'quantity': 2,
            'assigned_contact_ids': [str(self.foreign_contact.id)],
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_quantity_cannot_be_negative_or_below_assigned(self):
        vid = self._voip().data['id']
        self.assertEqual(self.client_.patch(f'/api/voip/{vid}/', {'quantity': -5}, format='json').status_code, 400)
        self.assertEqual(self.client_.patch(f'/api/voip/{vid}/', {'quantity': 1}, format='json').status_code, 400)

    def test_deleted_contact_frees_its_license(self):
        vid = self._voip().data['id']
        self.client_.delete(f'/api/contacts/{self.c1.id}/')
        data = self.client_.get(f'/api/voip/{vid}/').data
        self.assertEqual(data['assigned_count'], 1)
        self.assertEqual(data['available_licenses'], 1)
        self.assertEqual(len(data['assigned_contacts']), 1)

    def test_location_and_host_must_belong_to_same_organization(self):
        location = Location.objects.create(
            organization=self.foreign_org, name='L', address='a', city='c', postal_code='1', country='z'
        )
        bad = self.client_.post('/api/servers/', {
            'organization': str(self.org.id), 'name': 's', 'location': str(location.id),
        }, format='json')
        self.assertEqual(bad.status_code, 400)
        server = self.client_.post('/api/servers/', {'organization': str(self.org.id), 'name': 's'}, format='json')
        loop = self.client_.patch(
            f"/api/servers/{server.data['id']}/", {'host_server': server.data['id']}, format='json'
        )
        self.assertEqual(loop.status_code, 400)

    def test_password_starting_with_encryption_prefix_round_trips(self):
        created = self.client_.post('/api/passwords/', {
            'organization': str(self.org.id), 'name': 'odd', 'password': 'ENC::hello',
        }, format='json')
        stored = PasswordEntry.objects.get(pk=created.data['id']).password
        self.assertNotEqual(stored, 'ENC::hello')
        reveal = self.client_.post(f"/api/passwords/{created.data['id']}/retrieve_password/")
        self.assertEqual(reveal.status_code, 200)
        self.assertEqual(reveal.data['password'], 'ENC::hello')


class PerformanceTests(ReviewFixesBase):
    def test_list_and_diagram_queries_do_not_grow_with_rows(self):
        for i in range(5):
            Server.objects.create(organization=self.org, name=f's{i}', created_by=self.user)
        with CaptureQueriesContext(connection) as small_list:
            self.client_.get('/api/servers/')
        with CaptureQueriesContext(connection) as small_diagram:
            self.client_.get(f'/api/diagram/data/?organization_id={self.org.id}')
        for i in range(5, 40):
            Server.objects.create(organization=self.org, name=f's{i}', created_by=self.user)
            Software.objects.create(organization=self.org, name=f'sw{i}', created_by=self.user)
        with CaptureQueriesContext(connection) as big_list:
            self.client_.get('/api/servers/')
        with CaptureQueriesContext(connection) as big_diagram:
            self.client_.get(f'/api/diagram/data/?organization_id={self.org.id}')
        self.assertEqual(len(big_list), len(small_list))
        self.assertLessEqual(len(big_diagram), len(small_diagram) + 4)

    def test_page_size_parameter_is_honoured(self):
        for i in range(60):
            Organization.objects.create(name=f'o{i}')
        response = self.client_.get('/api/organizations/?page_size=1000')
        self.assertEqual(len(response.data['results']), response.data['count'])

    def test_invalid_ids_return_400_not_500(self):
        self.assertEqual(self.client_.get('/api/diagram/data/?organization_id=nope').status_code, 400)
        self.assertEqual(self.client_.get('/api/endpoints/counts/?organization_id=nope').status_code, 400)
        self.assertEqual(self.client_.get('/api/servers/by_organization/?organization_id=nope').status_code, 400)
