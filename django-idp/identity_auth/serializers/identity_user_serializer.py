"""Serializer de salida para el árbol de identidad del usuario."""

from rest_framework import serializers


class IdentityUserSerializer(serializers.Serializer):
    """Representación compacta de identidad devuelta por el IdP."""

    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.CharField(allow_blank=True)
    is_active = serializers.BooleanField()
    groups = serializers.ListField()
    permissions = serializers.ListField()
