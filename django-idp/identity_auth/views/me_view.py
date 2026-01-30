from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from ..serializers import IdentityUserSerializer
from ._identity_payload import _identity_payload


@extend_schema(
    summary="Me (devuelve identidad según sesión del IdP)",
    responses=IdentityUserSerializer,
)
@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def me_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return Response({"detail": "No autenticado"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    return Response(_identity_payload(user), status=status.HTTP_200_OK)
