"""Serializer de entrada para registrar usuarios."""

from rest_framework import serializers


class RegisterRequestSerializer(serializers.Serializer):
    """Valida campos mínimos para creación de usuario."""

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
