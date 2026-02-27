"""Serializer de salida para endpoint de CSRF."""

from rest_framework import serializers


class CsrfResponseSerializer(serializers.Serializer):
    """Entrega token CSRF inicial para clientes externos."""

    csrfToken = serializers.CharField()
