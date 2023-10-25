from rest_framework import serializers

from common.fields import HeadlineField
from common.serializers import DetailsSerializer
from file_manager.serializers import DocumentTypeSerializer, SubjectSerializer


class ContentSearchSerializer(DetailsSerializer, serializers.Serializer):
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
    # content_type = serializers.CharField()
    # content_id = serializers.IntegerField()
    document_name_headline = HeadlineField()
    summary_headline = HeadlineField()


class ContentListSerializer(DetailsSerializer, serializers.Serializer, ):
    uid = serializers.CharField()
    doc_name_string = serializers.CharField()
    file_name_string = serializers.CharField()
    date_string = serializers.DateField()
    content = serializers.CharField()
    summary_string = serializers.CharField()
    locations = serializers.SerializerMethodField()
    document_type = DocumentTypeSerializer(many=False, read_only=True)
    resource_type = serializers.CharField()
    subjects = SubjectSerializer(many=True, read_only=True)
    category = serializers.SerializerMethodField()
    url = serializers.CharField()
    # content_type = serializers.CharField()
    # content_id = serializers.IntegerField()


class ContentUpdateSerializer(serializers.Serializer):
    id = serializers.CharField()
    text = serializers.CharField()
