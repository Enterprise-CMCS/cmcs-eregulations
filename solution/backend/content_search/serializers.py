from rest_framework import serializers

from common.fields import HeadlineField
from common.serializers.mix import DetailsSerializer
from file_manager.serializers.groupings import DocumentTypeSerializer, SubjectSerializer


class ContentListSerializer(DetailsSerializer, serializers.Serializer, ):
    doc_name_string = serializers.CharField()
    file_name_string = serializers.CharField()
    date_string = serializers.DateField()
    summary_string = serializers.CharField()
    locations = serializers.SerializerMethodField()
    document_type = DocumentTypeSerializer(many=False, read_only=True)
    resource_type = serializers.CharField()
    subjects = SubjectSerializer(many=True, read_only=True)
    category = serializers.SerializerMethodField()
    url = serializers.CharField()
    id = serializers.IntegerField()
    document_name_headline = HeadlineField()
    summary_headline = HeadlineField()


class ContentSearchSerializer(ContentListSerializer, ):
    document_name_headline = HeadlineField()
    summary_headline = HeadlineField()
    content_headline = HeadlineField()


class ContentUpdateSerializer(serializers.Serializer):
    id = serializers.CharField()
    text = serializers.CharField()
