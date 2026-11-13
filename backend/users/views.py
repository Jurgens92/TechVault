from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer, AdminUserSerializer, UserCreateSerializer, _validate_new_password
)
from .utils import get_client_ip

User = get_user_model()


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    View to retrieve and update the current user's profile.
    Role/status fields (is_staff, is_active) are read-only here.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserManagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users. Only accessible by admin users.
    Provides list, create, retrieve, update, and delete operations, plus
    account recovery actions (reset password, reset 2FA, unlock).
    """
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return AdminUserSerializer

    def _audit(self, action_name, target, details='', changes=None):
        from core.models import AuditLog
        AuditLog.log(
            user=self.request.user,
            action=action_name,
            entity_type='User',
            entity_id=target.pk,
            entity_name=target.email,
            details=details,
            changes=changes,
            ip_address=get_client_ip(self.request),
        )

    def _other_active_admins_exist(self, instance):
        return User.objects.filter(is_staff=True, is_active=True).exclude(pk=instance.pk).exists()

    def perform_create(self, serializer):
        user = serializer.save()
        self._audit('create', user, changes={'fields': [
            {'field': 'email', 'value': user.email},
            {'field': 'is_staff', 'value': user.is_staff},
            {'field': 'is_active', 'value': user.is_active},
        ]})

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        losing_admin = (
            instance.is_staff and instance.is_active and (
                request.data.get('is_staff') in (False, 'false', 'False') or
                request.data.get('is_active') in (False, 'false', 'False')
            )
        )
        if losing_admin:
            if instance == request.user:
                return Response(
                    {'detail': 'You cannot remove your own administrator access or deactivate your own account.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not self._other_active_admins_exist(instance):
                return Response(
                    {'detail': 'At least one active administrator is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        tracked = ['email', 'first_name', 'last_name', 'is_active', 'is_staff']
        before = {f: getattr(serializer.instance, f) for f in tracked}
        user = serializer.save()
        diff = [
            {'field': f, 'old': before[f], 'new': getattr(user, f)}
            for f in tracked if before[f] != getattr(user, f)
        ]
        self._audit('update', user, changes={'diff': diff} if diff else None)

    def destroy(self, request, *args, **kwargs):
        """
        Prevent users from deleting themselves or the last administrator.
        """
        instance = self.get_object()
        if instance == request.user:
            return Response(
                {"detail": "You cannot delete your own account."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if instance.is_staff and instance.is_active and not self._other_active_admins_exist(instance):
            return Response(
                {"detail": "At least one active administrator is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        self._audit('delete', instance)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='reset-password')
    def reset_password(self, request, pk=None):
        """Set a new password for a user (admin account recovery)."""
        target = self.get_object()
        password = request.data.get('password') or ''
        if not password:
            return Response({'password': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)
        from rest_framework import serializers as drf_serializers
        try:
            _validate_new_password(password, target)
        except drf_serializers.ValidationError as e:
            return Response({'password': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        target.set_password(password)
        target.failed_login_attempts = 0
        target.locked_until = None
        target.save(update_fields=['password', 'failed_login_attempts', 'locked_until'])
        self._audit('update', target, details='Password reset by administrator')
        return Response({'detail': 'Password has been reset.'})

    @action(detail=True, methods=['post'], url_path='reset-2fa')
    def reset_2fa(self, request, pk=None):
        """
        Clear a user's 2FA enrolment (e.g. lost authenticator and no backup codes).
        The user is required to set 2FA up again at their next login.
        """
        target = self.get_object()
        target.twofa_enabled = False
        target.twofa_secret = None
        target.twofa_backup_codes = []
        target.save(update_fields=['twofa_enabled', 'twofa_secret', 'twofa_backup_codes'])
        self._audit('update', target, details='Two-factor authentication reset by administrator')
        return Response({'detail': 'Two-factor authentication has been reset. The user must set it up again at next login.'})

    @action(detail=True, methods=['post'])
    def unlock(self, request, pk=None):
        """Clear an account lockout caused by failed login attempts."""
        target = self.get_object()
        target.reset_failed_login_attempts()
        self._audit('update', target, details='Account unlocked by administrator')
        return Response({'detail': 'Account unlocked.'})
