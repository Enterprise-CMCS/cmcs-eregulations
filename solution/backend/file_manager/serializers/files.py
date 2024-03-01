
from rest_framework import serializers

from common.fields import HeadlineField
from common.serializers.mix import DetailsSerializer

from .groupings import DocumentTypeSerializer, SubjectSerializer
from .groups import DivisionWithGroupSerializer


class UploadedFileSerializer(DetailsSerializer, serializers.Serializer):
    document_name = serializers.CharField()
    file_name = serializers.CharField()
    date = serializers.DateField()
    summary = serializers.CharField()
    document_type = DocumentTypeSerializer(many=False, read_only=True)
    locations = serializers.SerializerMethodField()
    subjects = SubjectSerializer(many=True, read_only=True)
    division = DivisionWithGroupSerializer()
    uid = serializers.CharField()

    document_name_headline = HeadlineField()
    summary_headline = HeadlineField()


class AwsTokenSerializer(serializers.Serializer):
    url = serializers.CharField()
    fields = serializers.JSONField()
