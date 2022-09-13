from rest_framework import serializers


class PartsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    date = serializers.CharField()
    last_updated = serializers.CharField()
    depth = serializers.IntegerField()


class VersionsSerializer(serializers.Serializer):
    date = serializers.CharField()
    part_name = serializers.ListField(child=serializers.CharField())


class StringListSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return instance
