from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from ..serializers import LoginRequestSerializer, LoginResponseSerializer
from ._identity_payload import _identity_payload


@extend_schema(
    summary="Login (valida credenciales y retorna identidad + árbol)",
    request=LoginRequestSerializer,
    responses=LoginResponseSerializer,
)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def login_view(request):
    serializer = LoginRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data["username"]
    password = serializer.validated_data["password"]

    user = authenticate(username=username, password=password)

    if not user:
        return Response({"detail": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.is_active:
        return Response({"detail": "Usuario inactivo"}, status=status.HTTP_403_FORBIDDEN)

    # Sesión IdP (no token)
    request.session["user_id"] = user.id

    return Response(
        {"user": _identity_payload(user), "session_active": True},
        status=status.HTTP_200_OK,
    )
