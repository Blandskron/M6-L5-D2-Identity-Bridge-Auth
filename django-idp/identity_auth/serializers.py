from rest_framework import serializers


class RegisterRequestSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)


class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)


class IdentityUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.CharField(allow_blank=True)
    is_active = serializers.BooleanField()
    groups = serializers.ListField()
    permissions = serializers.ListField()


class LoginResponseSerializer(serializers.Serializer):
    user = IdentityUserSerializer()
    session_active = serializers.BooleanField()


class LogoutResponseSerializer(serializers.Serializer):
    logged_out = serializers.BooleanField()


class CsrfResponseSerializer(serializers.Serializer):
    csrfToken = serializers.CharField()
