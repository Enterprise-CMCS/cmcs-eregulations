from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field


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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request', None)

        # Serialize resources by full representation if requested
        if request and request.query_params.get('serialize_by') == 'full':
            resource_serializer = ResourceSerializer(instance.resources.all(), many=True)
            representation['resources'] = resource_serializer.data

        return representation
