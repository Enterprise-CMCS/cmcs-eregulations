from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from common.fields import HeadlineField
from resources.serializers.locations import AbstractLocationPolymorphicSerializer, MetaLocationSerializer

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

    class Meta:
        model = Subject


class UploadedFileSerializer(serializers.Serializer, ):
    name = serializers.CharField()
    file_name = serializers.CharField()
    date = serializers.DateField()
    description = serializers.CharField()
    locations = serializers.SerializerMethodField()
    document_type = DocumentTypeSerializer(many=False, read_only=True)
    subject = SubjectSerializer(many=True, read_only=True)
    uid = serializers.CharField()

    name_headline = HeadlineField()
    description_headline = HeadlineField()

    @extend_schema_field(MetaLocationSerializer.many(True))
    def get_locations(self, obj):
        if self.context.get("location_details", True):
            return AbstractLocationPolymorphicSerializer(obj.locations, many=True).data
        return serializers.PrimaryKeyRelatedField(read_only=True, many=True).to_representation(obj.locations.all())


class AwsTokenSerializer(serializers.Serializer):
    url = serializers.CharField()
    fields = serializers.JSONField()
