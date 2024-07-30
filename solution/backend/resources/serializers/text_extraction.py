from rest_framework import serializers


class ContentUpdateSerializer(serializers.Serializer):
    text = serializers.CharField()
