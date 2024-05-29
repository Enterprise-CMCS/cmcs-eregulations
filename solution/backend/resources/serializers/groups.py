from rest_framework import serializers


class ResourceGroupSerializer(serializers.Serializer):
    name = serializers.CharField()
    common_identifiers = serializers.ListField(child=serializers.CharField())
    resources = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  # TODO: serialize the whole resource
