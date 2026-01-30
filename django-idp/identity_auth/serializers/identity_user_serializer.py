from rest_framework import serializers


class IdentityUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.CharField(allow_blank=True)
    is_active = serializers.BooleanField()
    groups = serializers.ListField()
    permissions = serializers.ListField()
