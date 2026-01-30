from rest_framework import serializers
from .identity_user_serializer import IdentityUserSerializer


class LoginResponseSerializer(serializers.Serializer):
    user = IdentityUserSerializer()
    session_active = serializers.BooleanField()
