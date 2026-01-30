from rest_framework import serializers


class CsrfResponseSerializer(serializers.Serializer):
    csrfToken = serializers.CharField()
