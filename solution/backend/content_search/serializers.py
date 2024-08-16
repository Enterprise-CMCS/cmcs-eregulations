from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from common.fields import HeadlineField
from resources.serializers import AbstractResourceSerializer


class ContentSearchSerializer(serializers.Serializer):
    name_headline = HeadlineField()
    summary_headline = HeadlineField()
    content_headline = HeadlineField(blank_when_no_highlight=True)

    resource = AbstractResourceSerializer()

    @extend_schema_field(serializers.IntegerField())
    def get_reg_text(self, obj):
        return obj.reg_text.id if obj.reg_text else None

    reg_text = serializers.SerializerMethodField()


class ContentUpdateSerializer(serializers.Serializer):
    id = serializers.CharField()
    text = serializers.CharField()
