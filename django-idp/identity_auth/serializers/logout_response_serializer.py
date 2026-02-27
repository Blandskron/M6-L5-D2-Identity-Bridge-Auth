"""Serializer de salida para logout."""

from rest_framework import serializers


class LogoutResponseSerializer(serializers.Serializer):
    """Indica si la sesión fue revocada correctamente."""

    logged_out = serializers.BooleanField()
