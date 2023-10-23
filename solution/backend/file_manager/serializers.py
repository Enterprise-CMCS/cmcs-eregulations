from rest_framework import serializers

from common.fields import HeadlineField
from common.serializers import DetailsSerializer

from .models import DocumentType, Subject


class DocumentTypeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()

    class Meta:
        model = DocumentType


class SubjectSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    short_name = serializers.CharField()
    abbreviation = serializers.CharField()


class SubjectDetailsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    short_name = serializers.CharField()
    abbreviation = serializers.CharField()
    content = serializers.SerializerMethodField()
    internal_content = serializers.IntegerField()
    external_content = serializers.IntegerField()

    def get_content(self, obj):
        return obj.content.count()

    class Meta:
        model = Subject


class UploadedFileSerializer(DetailsSerializer, serializers.Serializer, ):
    document_name = serializers.CharField()
    file_name = serializers.CharField()
    date = serializers.DateField()
    summary = serializers.CharField()
    document_type = DocumentTypeSerializer(many=False, read_only=True)
    locations = serializers.SerializerMethodField()
    subjects = SubjectSerializer(many=True, read_only=True)
    uid = serializers.CharField()

    document_name_headline = HeadlineField()
    summary_headline = HeadlineField()


class AwsTokenSerializer(serializers.Serializer):
    url = serializers.CharField()
    fields = serializers.JSONField()
