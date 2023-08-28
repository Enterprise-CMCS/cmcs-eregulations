from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from resources.serializers.locations import MetaLocationSerializer

from .models import Subject, UploadCategory


class UploadCategorySerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()

    class Meta:
        model = UploadCategory


class SubjectSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()

    class Meta:
        model = Subject

#     fields = ("nsassmess", "fsiless", d'dsate', 'desscription', 'categoriess', 'subject', 'locations', 'download_file',)


class UploadedFileSerializer(serializers.Serializer):
    name = serializers.CharField()
    date = serializers.DateField()
    description = serializers.CharField()
    locations = serializers.SerializerMethodField()
    categories = UploadCategorySerializer(many=True, read_only=True)
    subject = SubjectSerializer(many=True, read_only=True)
    uid = serializers.CharField()

    @extend_schema_field(MetaLocationSerializer.many(True))
    def get_locations(self, obj):
        return serializers.PrimaryKeyRelatedField(read_only=True, many=True).to_representation(obj.locations.all())
