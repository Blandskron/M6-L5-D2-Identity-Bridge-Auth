"""Serializer de entrada para login."""

from rest_framework import serializers


class LoginRequestSerializer(serializers.Serializer):
    """Valida credenciales entregadas por cliente."""

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
