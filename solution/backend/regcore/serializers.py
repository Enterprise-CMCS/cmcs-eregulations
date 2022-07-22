from rest_framework import serializers
from regcore.search.models import Synonym

from .models import Title, ECFRParserResult


class FlatContentsSerializer(serializers.Serializer):
    type = serializers.CharField()
    label = serializers.CharField()
    parent = serializers.ListField(child=serializers.CharField(), allow_null=True, allow_empty=True)
    reserved = serializers.BooleanField()
    identifier = serializers.ListField(child=serializers.CharField())
    label_level = serializers.CharField()
    parent_type = serializers.CharField(allow_blank=True)
    descendant_range = serializers.ListField(child=serializers.CharField(), allow_null=True, allow_empty=True)
    label_description = serializers.CharField()


class ContentsSerializer(FlatContentsSerializer):
    def get_fields(self):
        fields = super(ContentsSerializer, self).get_fields()
        fields['children'] = serializers.ListField(child=ContentsSerializer(), allow_null=True, allow_empty=True)
        return fields


class TitlesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    last_updated = serializers.CharField()


class TitleRetrieveSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    last_updated = serializers.CharField()
    toc = ContentsSerializer()


class TitleUploadSerializer(serializers.ModelSerializer):
    toc = ContentsSerializer()

    class Meta:
        model = Title
        fields = ["name", "toc"]


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


class ParserResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ECFRParserResult
        fields = '__all__'

class SynonymSerializer(serializers.Serializer):
    baseWord = serializers.CharField()
    isActive = serializers.BooleanField()

class SynonymsSerializer(serializers.Serializer):
    isActive = serializers.BooleanField()
    baseWord = serializers.CharField()
    synonyms= SynonymSerializer(read_only=True, many=True)
    
    class Meta:
        model = Synonym
        fields = ('__all__')