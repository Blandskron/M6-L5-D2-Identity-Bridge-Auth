from rest_framework import serializers


class LogoutResponseSerializer(serializers.Serializer):
    logged_out = serializers.BooleanField()
