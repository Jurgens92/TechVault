"""
Organization membership model for access control.
Implements multi-tenant data isolation by linking users to organizations.
"""
from django.db import models
from django.conf import settings
from .base import BaseModel
from .organization import Organization


class OrganizationMember(BaseModel):
    """
    Links users to organizations they have access to.
    This is the foundation for multi-tenant access control.
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='members'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organization_memberships'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='member'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'organization_members'
        unique_together = ('organization', 'user')
        ordering = ['organization', 'user']

    def __str__(self):
        return f"{self.user.email} - {self.organization.name} ({self.role})"

    @classmethod
    def get_user_organizations(cls, user):
        """Get all organizations a user has access to."""
        return Organization.objects.filter(
            members__user=user,
            members__is_active=True
        )

    @classmethod
    def user_has_access(cls, user, organization):
        """Check if a user has access to an organization."""
        return cls.objects.filter(
            user=user,
            organization=organization,
            is_active=True
        ).exists()

    @classmethod
    def get_user_role(cls, user, organization):
        """Get the user's role in an organization."""
        membership = cls.objects.filter(
            user=user,
            organization=organization,
            is_active=True
        ).first()
        return membership.role if membership else None
