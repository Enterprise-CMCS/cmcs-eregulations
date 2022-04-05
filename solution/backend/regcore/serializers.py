from rest_framework import serializers

from regcore.models import Title, Part


class ContentsSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return instance.toc


class TitlesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ("id", "name", "last_updated")


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = "__all__"


class PartsSerialier(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = ("id", "name", "date", "last_updated", "depth", "title_object")


class VersionsSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return instance.date
