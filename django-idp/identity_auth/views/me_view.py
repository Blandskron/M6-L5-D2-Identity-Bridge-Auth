"""Endpoint de introspección de identidad a partir de sesión activa."""

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from rest_framework.authentication import SessionAuthentication

from ..serializers import IdentityUserSerializer
from ._identity_payload import _identity_payload


@extend_schema(
    summary="Me (devuelve identidad según sesión del IdP)",
    responses=IdentityUserSerializer,
)
@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([])
def me_view(request):
    """Retorna identidad del usuario actualmente autenticado en sesión."""
    user = request.user
    if not user.is_authenticated:
        return Response({"detail": "No autenticado"}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(_identity_payload(user), status=status.HTTP_200_OK)
