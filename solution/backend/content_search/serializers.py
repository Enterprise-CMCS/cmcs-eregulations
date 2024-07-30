from rest_framework import serializers

from common.fields import HeadlineField
from resources.serializers import AbstractResourceSerializer


class ContentSearchSerializer(serializers.Serializer):
    name_headline = HeadlineField()
    summary_headline = HeadlineField()
    content_headline = HeadlineField(blank_when_no_highlight=True)

    resource = AbstractResourceSerializer()
    reg_text = serializers.PrimaryKeyRelatedField(read_only=True)
