from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from common.fields import HeadlineField
from file_manager.serializers import DocumentTypeSerializer, SubjectSerializer
from resources.serializers.locations import AbstractLocationPolymorphicSerializer, MetaLocationSerializer


class ContentSearchSerializer(serializers.Serializer, ):
    doc_name_string = serializers.CharField()
    file_name_string = serializers.CharField()
    date_string = serializers.DateField()
    summary_string = serializers.CharField()
    locations = serializers.SerializerMethodField()
    document_type = DocumentTypeSerializer(many=False, read_only=True)
    subject = SubjectSerializer(many=True, read_only=True)
    url = serializers.CharField()

    document_id_headline = HeadlineField()
    summary_headline = HeadlineField()

    @extend_schema_field(MetaLocationSerializer.many(True))
    def get_locations(self, obj):
        if self.context['request'].GET.get("location_details") == 'true':
            return AbstractLocationPolymorphicSerializer(obj.locations.all(), many=True).data
        return serializers.PrimaryKeyRelatedField(read_only=True, many=True).to_representation(obj.locations.all())
