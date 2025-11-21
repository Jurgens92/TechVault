from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


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
