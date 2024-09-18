from rest_framework import serializers

from .resources import AbstractResourceSerializer


class ResourceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class ResourceGroupSerializer(serializers.Serializer):
    name = serializers.CharField()
    common_identifiers = serializers.ListField(child=serializers.CharField())
    resources = AbstractResourceSerializer(many=True)
