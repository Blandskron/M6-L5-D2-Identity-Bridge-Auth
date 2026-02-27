"""Serializer de salida para respuesta de login."""

from rest_framework import serializers
from .identity_user_serializer import IdentityUserSerializer


class LoginResponseSerializer(serializers.Serializer):
    """Incluye identidad y bandera de sesión activa."""

    user = IdentityUserSerializer()
    session_active = serializers.BooleanField()
