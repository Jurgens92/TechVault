"""
System Backup/Restore service for complete system data backup including users and 2FA configs.
Security: Passwords are exported as hashed values and 2FA secrets are included for full restore capability.
"""
from datetime import datetime
import json
from typing import Dict, List, Any, Optional
import uuid
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from core.models import (
    Organization, Location, Contact, NetworkDevice, Server,
    EndpointUser, Peripheral, Software, VoIP, Backup,
    Documentation, Configuration, PasswordEntry,
    SoftwareAssignment, VoIPAssignment
)
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.dateparse import parse_datetime
from core.models import AuditLog
from core.encryption import (
    protect_encryption_key, recover_encryption_key,
    encrypt_with_password, decrypt_with_password,
)
from .export_import_service import OrganizationExportImportService

User = get_user_model()


class SystemBackupService:
    """Service for complete system backup and restore including users and 2FA configurations."""

    BACKUP_VERSION = '1.0'

    def __init__(self, user):
        """Initialize the service with the requesting user."""
        self.user = user
        self.org_export_service = OrganizationExportImportService(user)

    def create_backup(self, include_deleted: bool = False, backup_password: str = None) -> Dict[str, Any]:
        """
        Create a complete system backup including all data.

        Args:
            include_deleted: Whether to include soft-deleted records
            backup_password: Password to protect the encryption key in the backup

        Returns:
            Dictionary containing complete system backup data
        """
        backup_data = {
            'backup_version': self.BACKUP_VERSION,
            'backup_type': 'full_system',
            'created_at': datetime.now().isoformat(),
            'created_by': self.user.email,
            'include_deleted': include_deleted,
            'organizations': self._export_all_organizations(include_deleted),
        }

        users = self._export_users()
        audit_logs = self._export_audit_logs()
        if backup_password:
            backup_data['encryption_key_data'] = protect_encryption_key(backup_password)
            # User records contain password hashes and 2FA secrets, and the audit
            # log contains activity history: never write those to the file in clear.
            backup_data['users_encrypted'] = encrypt_with_password(
                json.dumps(users, cls=DjangoJSONEncoder).encode(), backup_password
            )
            backup_data['audit_logs_encrypted'] = encrypt_with_password(
                json.dumps(audit_logs, cls=DjangoJSONEncoder).encode(), backup_password
            )
        else:
            backup_data['users'] = users
            backup_data['audit_logs'] = audit_logs

        return backup_data

    def _export_users(self) -> List[Dict[str, Any]]:
        """
        Export all users with their 2FA configurations.
        Password hashes are included for restore capability.
        """
        users = User.objects.all()
        exported_users = []

        for user in users:
            user_data = {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'password_hash': user.password,  # Already hashed by Django
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                # 2FA Configuration
                'twofa_enabled': user.twofa_enabled,
                'twofa_secret': user.twofa_secret,  # TOTP secret for 2FA
                'twofa_backup_codes': user.twofa_backup_codes,  # Already hashed backup codes
                # Account security fields
                'failed_login_attempts': user.failed_login_attempts,
                'locked_until': user.locked_until.isoformat() if user.locked_until else None,
                'last_failed_login': user.last_failed_login.isoformat() if user.last_failed_login else None,
            }
            exported_users.append(user_data)

        return exported_users

    def _export_audit_logs(self) -> List[Dict[str, Any]]:
        """Export the audit trail so a restored system keeps its history."""
        return [
            {
                'id': str(log.id),
                'user_email': log.user.email if log.user else None,
                'action': log.action,
                'entity_type': log.entity_type,
                'entity_id': log.entity_id,
                'entity_name': log.entity_name,
                'organization_name': log.organization_name,
                'details': log.details,
                'changes': log.changes,
                'ip_address': log.ip_address,
                'timestamp': log.timestamp.isoformat(),
            }
            for log in AuditLog.objects.select_related('user').iterator()
        ]

    def _restore_audit_logs(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Restore audit entries that are not already present (matched by id)."""
        existing = set(str(pk) for pk in AuditLog.objects.values_list('id', flat=True))
        users = {u.email: u for u in User.objects.all()}
        restored = 0
        for entry in logs or []:
            try:
                if entry['id'] in existing:
                    continue
                log = AuditLog.objects.create(
                    id=uuid.UUID(entry['id']),
                    user=users.get(entry.get('user_email')),
                    action=entry['action'],
                    entity_type=entry.get('entity_type', ''),
                    entity_id=entry.get('entity_id', ''),
                    entity_name=entry.get('entity_name', ''),
                    organization_name=entry.get('organization_name', ''),
                    details=entry.get('details', ''),
                    changes=entry.get('changes'),
                    ip_address=entry.get('ip_address'),
                )
                timestamp = parse_datetime(entry['timestamp']) if entry.get('timestamp') else None
                if timestamp:
                    # timestamp is auto_now_add, so set the original value afterwards
                    AuditLog.objects.filter(pk=log.pk).update(timestamp=timestamp)
                restored += 1
            except Exception:
                continue
        return {'restored': restored}

    def _export_all_organizations(self, include_deleted: bool) -> List[Dict[str, Any]]:
        """Export all organizations with their complete data."""
        export_data = self.org_export_service.export_organizations(
            organization_ids=None,
            include_deleted=include_deleted
        )
        return export_data.get('organizations', [])

    def restore_backup(
        self,
        backup_data: Dict[str, Any],
        restore_users: bool = True,
        restore_organizations: bool = True,
        overwrite_existing: bool = False,
        backup_password: str = None
    ) -> Dict[str, Any]:
        """
        Restore system from a backup file.

        Args:
            backup_data: The backup data to restore from
            restore_users: Whether to restore user data
            restore_organizations: Whether to restore organization data
            overwrite_existing: Whether to overwrite existing records
            backup_password: Password to decrypt the encryption key from the backup

        Returns:
            Dictionary with restore results
        """
        results = {
            'success': True,
            'users': {
                'restored': [],
                'skipped': [],
                'errors': []
            },
            'organizations': {
                'imported': [],
                'skipped': [],
                'errors': []
            }
        }

        # Validate backup version
        backup_version = backup_data.get('backup_version', '0.0')
        if backup_version != self.BACKUP_VERSION:
            results['success'] = False
            results['error'] = f'Unsupported backup version: {backup_version}. Expected: {self.BACKUP_VERSION}'
            return results

        # Recover old encryption key if backup contains key data
        old_encryption_key = None
        if backup_data.get('encryption_key_data'):
            if not backup_password:
                results['success'] = False
                results['error'] = 'This backup is password-protected. Please provide the backup password.'
                return results
            try:
                old_encryption_key = recover_encryption_key(
                    backup_password, backup_data['encryption_key_data']
                )
            except Exception as e:
                results['success'] = False
                results['error'] = f'Failed to unlock backup: {str(e)}'
                return results

        # Unlock the password-protected sections (newer backups)
        users_data = backup_data.get('users')
        audit_logs_data = backup_data.get('audit_logs')
        try:
            if backup_data.get('users_encrypted'):
                if not backup_password:
                    raise ValueError('This backup is password-protected. Please provide the backup password.')
                users_data = json.loads(decrypt_with_password(backup_data['users_encrypted'], backup_password))
            if backup_data.get('audit_logs_encrypted') and backup_password:
                audit_logs_data = json.loads(
                    decrypt_with_password(backup_data['audit_logs_encrypted'], backup_password)
                )
        except Exception as e:
            results['success'] = False
            results['error'] = f'Failed to unlock backup: {str(e)}'
            return results

        # Restore users first (organizations may reference them)
        if restore_users and users_data is not None:
            user_results = self._restore_users(
                users_data,
                overwrite_existing
            )
            results['users'] = user_results

        # Restore organizations. Vault passwords in the backup are re-encrypted
        # with this server's key as they are imported (only the imported entries
        # are touched - existing data is already under the current key).
        if restore_organizations and 'organizations' in backup_data:
            org_results = self._restore_organizations(
                backup_data['organizations'],
                overwrite_existing,
                old_encryption_key
            )
            results['organizations'] = org_results

        # Restore the audit trail (entries already present are left alone)
        if audit_logs_data:
            results['audit_logs'] = self._restore_audit_logs(audit_logs_data)

        # Determine overall success
        results['success'] = (
            len(results['users'].get('errors', [])) == 0 and
            len(results['organizations'].get('errors', [])) == 0
        )

        return results

    @transaction.atomic
    def _restore_users(
        self,
        users_data: List[Dict[str, Any]],
        overwrite_existing: bool
    ) -> Dict[str, Any]:
        """
        Restore users from backup data.

        Args:
            users_data: List of user data dictionaries
            overwrite_existing: Whether to update existing users

        Returns:
            Dictionary with restore results for users
        """
        results = {
            'restored': [],
            'skipped': [],
            'errors': []
        }

        for user_data in users_data:
            try:
                email = user_data['email']
                existing_user = User.objects.filter(email=email).first()

                if existing_user:
                    if overwrite_existing:
                        # Update existing user
                        self._update_user_from_backup(existing_user, user_data)
                        results['restored'].append({
                            'email': email,
                            'action': 'updated'
                        })
                    else:
                        results['skipped'].append({
                            'email': email,
                            'reason': 'User already exists and overwrite is disabled'
                        })
                else:
                    # Create new user
                    self._create_user_from_backup(user_data)
                    results['restored'].append({
                        'email': email,
                        'action': 'created'
                    })

            except Exception as e:
                results['errors'].append({
                    'email': user_data.get('email', 'unknown'),
                    'error': str(e)
                })

        return results

    def _create_user_from_backup(self, user_data: Dict[str, Any]) -> User:
        """Create a new user from backup data."""
        user = User(
            email=user_data['email'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            password=user_data['password_hash'],  # Already hashed
            is_active=user_data.get('is_active', True),
            is_staff=user_data.get('is_staff', False),
            # Only a superuser may create superusers through a restore
            is_superuser=bool(user_data.get('is_superuser', False)) and self.user.is_superuser,
            # 2FA Configuration
            twofa_enabled=user_data.get('twofa_enabled', False),
            twofa_secret=user_data.get('twofa_secret'),
            twofa_backup_codes=user_data.get('twofa_backup_codes', []),
            # Account security
            failed_login_attempts=user_data.get('failed_login_attempts', 0),
        )

        # Handle datetime fields
        if user_data.get('locked_until'):
            from django.utils.dateparse import parse_datetime
            user.locked_until = parse_datetime(user_data['locked_until'])

        if user_data.get('last_failed_login'):
            from django.utils.dateparse import parse_datetime
            user.last_failed_login = parse_datetime(user_data['last_failed_login'])

        user.save()
        return user

    def _update_user_from_backup(self, user: User, user_data: Dict[str, Any]) -> User:
        """Update an existing user from backup data."""
        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        user.password = user_data['password_hash']  # Replace with backup password hash
        user.is_active = user_data.get('is_active', user.is_active)
        user.is_staff = user_data.get('is_staff', user.is_staff)
        if self.user.is_superuser:
            user.is_superuser = user_data.get('is_superuser', user.is_superuser)
        elif user.is_superuser:
            # A staff (non-superuser) admin must not be able to take over a
            # superuser account by restoring a crafted backup.
            raise PermissionError('Only a superuser can overwrite a superuser account')

        # 2FA Configuration
        user.twofa_enabled = user_data.get('twofa_enabled', False)
        user.twofa_secret = user_data.get('twofa_secret')
        user.twofa_backup_codes = user_data.get('twofa_backup_codes', [])

        # Account security
        user.failed_login_attempts = user_data.get('failed_login_attempts', 0)

        # Handle datetime fields
        if user_data.get('locked_until'):
            from django.utils.dateparse import parse_datetime
            user.locked_until = parse_datetime(user_data['locked_until'])
        else:
            user.locked_until = None

        if user_data.get('last_failed_login'):
            from django.utils.dateparse import parse_datetime
            user.last_failed_login = parse_datetime(user_data['last_failed_login'])
        else:
            user.last_failed_login = None

        user.save()
        return user

    def _restore_organizations(
        self,
        organizations_data: List[Dict[str, Any]],
        overwrite_existing: bool,
        source_encryption_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Restore organizations from backup data.

        Args:
            organizations_data: List of organization data from backup
            overwrite_existing: Whether to overwrite existing organizations

        Returns:
            Dictionary with restore results
        """
        # Reconstruct the import data format expected by the org service
        import_data = {
            'organizations': organizations_data
        }

        result = self.org_export_service.import_organizations(
            import_data=import_data,
            overwrite_existing=overwrite_existing,
            preserve_ids=False,
            source_encryption_key=source_encryption_key
        )

        restored = {
            'imported': result.get('imported_organizations', []),
            'skipped': result.get('skipped_organizations', []),
            'errors': result.get('errors', [])
        }
        if result.get('warning'):
            restored['warning'] = result['warning']
        return restored
