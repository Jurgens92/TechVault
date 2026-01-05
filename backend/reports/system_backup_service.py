"""
System Backup/Restore service for complete system data backup including users and 2FA configs.
Security: Passwords are exported as hashed values and 2FA secrets are included for full restore capability.
"""
from datetime import datetime
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
from core.encryption import encrypt_password, is_encrypted
from .export_import_service import OrganizationExportImportService

User = get_user_model()


class SystemBackupService:
    """Service for complete system backup and restore including users and 2FA configurations."""

    BACKUP_VERSION = '1.0'

    def __init__(self, user):
        """Initialize the service with the requesting user."""
        self.user = user
        self.org_export_service = OrganizationExportImportService(user)

    def create_backup(self, include_deleted: bool = False) -> Dict[str, Any]:
        """
        Create a complete system backup including all data.

        Args:
            include_deleted: Whether to include soft-deleted records

        Returns:
            Dictionary containing complete system backup data
        """
        backup_data = {
            'backup_version': self.BACKUP_VERSION,
            'backup_type': 'full_system',
            'created_at': datetime.now().isoformat(),
            'created_by': self.user.email,
            'include_deleted': include_deleted,
            'users': self._export_users(),
            'organizations': self._export_all_organizations(include_deleted),
        }

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
        overwrite_existing: bool = False
    ) -> Dict[str, Any]:
        """
        Restore system from a backup file.

        Args:
            backup_data: The backup data to restore from
            restore_users: Whether to restore user data
            restore_organizations: Whether to restore organization data
            overwrite_existing: Whether to overwrite existing records

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

        # Restore users first (organizations may reference them)
        if restore_users and 'users' in backup_data:
            user_results = self._restore_users(
                backup_data['users'],
                overwrite_existing
            )
            results['users'] = user_results

        # Restore organizations
        if restore_organizations and 'organizations' in backup_data:
            org_results = self._restore_organizations(
                backup_data['organizations'],
                overwrite_existing
            )
            results['organizations'] = org_results

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
            is_superuser=user_data.get('is_superuser', False),
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
        user.is_superuser = user_data.get('is_superuser', user.is_superuser)

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
        overwrite_existing: bool
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
            preserve_ids=False
        )

        return {
            'imported': result.get('imported_organizations', []),
            'skipped': result.get('skipped_organizations', []),
            'errors': result.get('errors', [])
        }
