from rest_framework import serializers


class FlatContentsSerializer(serializers.Serializer):
    type = serializers.CharField()
    label = serializers.CharField()
    parent = serializers.ListField(child=serializers.CharField())
    reserved = serializers.BooleanField()
    identifier = serializers.ListField(child=serializers.CharField())
    label_level = serializers.CharField()
    parent_type = serializers.CharField()
    descendant_range = serializers.ListField(child=serializers.CharField())
    label_description = serializers.CharField()


class ContentsSerializer(FlatContentsSerializer):
    def get_fields(self):
        fields = super(ContentsSerializer, self).get_fields()
        fields['children'] = serializers.ListField(child=ContentsSerializer())
        return fields


class TitlesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    last_updated = serializers.CharField()


class TitleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    last_updated = serializers.CharField()
    toc = ContentsSerializer()


class PartsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    date = serializers.CharField()
    last_updated = serializers.CharField()
    depth = serializers.IntegerField()
    title_object = serializers.IntegerField()


class VersionsSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return instance
