"""Endpoint para revocar la sesión actual del Identity Provider."""

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from ..serializers import LogoutResponseSerializer


@extend_schema(
    summary="Logout (revoca la sesión del IdP)",
    responses=LogoutResponseSerializer,
)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def logout_view(request):
    """Elimina completamente la sesión del cliente autenticado."""
    request.session.flush()
    return Response({"logged_out": True}, status=status.HTTP_200_OK)
