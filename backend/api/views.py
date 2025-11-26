from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import (
    Organization, Location, Contact, Documentation,
    PasswordEntry, Configuration
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def health_check(request):
    """
    Simple health check endpoint to verify authentication.
    """
    return Response({
        'status': 'ok',
        'user': request.user.email,
        'message': 'TechVault API is running'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics for all entities.
    """
    return Response({
        'organizations': Organization.objects.count(),
        'locations': Location.objects.count(),
        'contacts': Contact.objects.count(),
        'documentations': Documentation.objects.count(),
        'passwords': PasswordEntry.objects.count(),
        'configurations': Configuration.objects.count(),
    })
