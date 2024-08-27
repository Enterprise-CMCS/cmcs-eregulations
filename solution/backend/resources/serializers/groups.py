from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers


class ResourceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class ResourceGroupSerializer(serializers.Serializer):
    name = serializers.CharField()
    common_identifiers = serializers.ListField(child=serializers.CharField())

    @extend_schema_field(serializers.ListField(child=serializers.IntegerField()))
    def get_resources(self, obj):
        # Default behavior: return primary keys
        return [resource.id for resource in obj.resources.all()]

    resources = serializers.SerializerMethodField()
