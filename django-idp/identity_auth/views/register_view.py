from django.contrib.auth.models import User, Group
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from ..serializers import RegisterRequestSerializer, IdentityUserSerializer
from ._identity_payload import _identity_payload


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
