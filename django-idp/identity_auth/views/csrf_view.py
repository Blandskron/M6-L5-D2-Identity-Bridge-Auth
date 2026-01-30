from django.middleware.csrf import get_token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from ..serializers import CsrfResponseSerializer


@extend_schema(
    summary="Obtener CSRF token (para integraciones basadas en sesión)",
    responses=CsrfResponseSerializer,
)
@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def csrf_view(request):
    """
    Devuelve un CSRF token y deja preparado el seteo de cookie csrftoken.
    Útil si vas a usar SessionAuthentication/CSRF desde otro servicio.
    """
    token = get_token(request)
    return Response({"csrfToken": token}, status=status.HTTP_200_OK)
