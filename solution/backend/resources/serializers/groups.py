from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .resources import (
    AbstractResourceSerializer,
    MetaResourceSerializer,
)


class ResourceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class ResourceGroupSerializer(serializers.Serializer):
    name = serializers.CharField()
    common_identifiers = serializers.ListField(child=serializers.CharField())
    resources = serializers.SerializerMethodField()

    @extend_schema_field(MetaResourceSerializer.many(True))
    def get_resources(self, obj):
        return AbstractResourceSerializer(instance=obj.resources, many=True).data
