"""
Custom permission classes for TechVault.
Implements organization-level and object-level access control.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOrganizationMember(BasePermission):
    """
    Permission class that checks if the user is a member of the organization
    associated with the object being accessed.
    """
    message = "You do not have access to this organization's data."

    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check if user has access to the object's organization."""
        from core.models import OrganizationMember, Organization

        # Superusers have full access
        if request.user.is_superuser:
            return True

        # Get the organization from the object
        if isinstance(obj, Organization):
            organization = obj
        elif hasattr(obj, 'organization'):
            organization = obj.organization
        else:
            # If no organization relationship, deny access
            return False

        # Check membership
        return OrganizationMember.user_has_access(request.user, organization)


class IsOrganizationAdmin(BasePermission):
    """
    Permission class that requires the user to be an admin or owner
    of the organization to perform write operations.
    """
    message = "You must be an organization admin to perform this action."

    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check if user is an admin of the object's organization."""
        from core.models import OrganizationMember, Organization

        # Superusers have full access
        if request.user.is_superuser:
            return True

        # Read operations allowed for all members
        if request.method in SAFE_METHODS:
            return IsOrganizationMember().has_object_permission(request, view, obj)

        # Get the organization from the object
        if isinstance(obj, Organization):
            organization = obj
        elif hasattr(obj, 'organization'):
            organization = obj.organization
        else:
            return False

        # Check if user is admin or owner
        role = OrganizationMember.get_user_role(request.user, organization)
        return role in ('admin', 'owner')


class IsOrganizationOwner(BasePermission):
    """
    Permission class that requires the user to be an owner
    of the organization for destructive operations.
    """
    message = "You must be an organization owner to perform this action."

    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check if user is an owner of the object's organization."""
        from core.models import OrganizationMember, Organization

        # Superusers have full access
        if request.user.is_superuser:
            return True

        # Get the organization from the object
        if isinstance(obj, Organization):
            organization = obj
        elif hasattr(obj, 'organization'):
            organization = obj.organization
        else:
            return False

        # Check if user is owner
        role = OrganizationMember.get_user_role(request.user, organization)
        return role == 'owner'
