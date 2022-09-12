from rest_framework import serializers

from .toc import TOCSerializer


class TitleRetrieveSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    last_updated = serializers.CharField()
    toc = TOCSerializer()


class PartsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    date = serializers.CharField()
    last_updated = serializers.CharField()
    depth = serializers.IntegerField()
    title_object = serializers.IntegerField()


class StringListSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return instance
