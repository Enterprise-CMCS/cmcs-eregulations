from rest_framework import serializers


class PartsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    date = serializers.CharField()
    last_updated = serializers.CharField()
    depth = serializers.IntegerField()


class StringListSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return instance
