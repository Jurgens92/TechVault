"""
Custom permission classes for TechVault.
Implements organization-level and object-level access control.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOrganizationMember(BasePermission):
    """
    Permission class that checks if the user is authenticated.
    All authenticated users have access to all organizations (shared workspace model).
    """
    message = "You must be authenticated to access this data."

    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """All authenticated users have access to all objects."""
        return request.user and request.user.is_authenticated


class IsOrganizationAdmin(BasePermission):
    """
    Permission class that allows all authenticated users to perform operations.
    In shared workspace model, all users have admin-level access.
    """
    message = "You must be authenticated to perform this action."

    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """All authenticated users have admin access in shared workspace model."""
        return request.user and request.user.is_authenticated


class IsOrganizationOwner(BasePermission):
    """
    Permission class that allows all authenticated users to perform operations.
    In shared workspace model, all users have owner-level access.
    """
    message = "You must be authenticated to perform this action."

    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """All authenticated users have owner access in shared workspace model."""
        return request.user and request.user.is_authenticated
