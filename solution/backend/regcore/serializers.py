from rest_framework import serializers

from regcore.models import Title, Part


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


class TitlesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ("id", "name", "last_updated")


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = "__all__"


class PartsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = ("id", "name", "date", "last_updated", "depth", "title_object")


class VersionsSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return instance
