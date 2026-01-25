from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group
from django.middleware.csrf import get_token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from .serializers import (
    RegisterRequestSerializer,
    LoginRequestSerializer,
    LoginResponseSerializer,
    IdentityUserSerializer,
    LogoutResponseSerializer,
    CsrfResponseSerializer,
)


def _identity_payload(user: User):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email or "",
        "is_active": user.is_active,
        "groups": [
            {
                "name": g.name,
                "permissions": list(g.permissions.values("codename", "name")),
            }
            for g in user.groups.all()
        ],
        "permissions": list(user.user_permissions.values("codename", "name")),
    }


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


@extend_schema(
    summary="Registro de usuario (Django crea usuario y asigna grupo base)",
    request=RegisterRequestSerializer,
    responses=IdentityUserSerializer,
)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def register_view(request):
    serializer = RegisterRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data["username"]
    password = serializer.validated_data["password"]
    email = serializer.validated_data.get("email", "")

    if User.objects.filter(username=username).exists():
        return Response({"detail": "El username ya existe"}, status=status.HTTP_409_CONFLICT)

    user = User.objects.create_user(username=username, email=email, password=password)

    group, _ = Group.objects.get_or_create(name="user")
    user.groups.add(group)

    return Response(_identity_payload(user), status=status.HTTP_201_CREATED)


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


@extend_schema(
    summary="Logout (revoca la sesión del IdP)",
    responses=LogoutResponseSerializer,
)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def logout_view(request):
    request.session.flush()
    return Response({"logged_out": True}, status=status.HTTP_200_OK)
