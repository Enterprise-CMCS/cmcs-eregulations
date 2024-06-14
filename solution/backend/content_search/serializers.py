from rest_framework import serializers

from common.fields import HeadlineField


class ContentSearchSerializer(serializers.Serializer):
    name_headline = HeadlineField()
    summary_headline = HeadlineField()
    content_headline = HeadlineField(blank_when_no_highlight=True)

    resource = serializers.PrimaryKeyRelatedField(read_only=True)
    reg_text = serializers.PrimaryKeyRelatedField(read_only=True)


class ContentUpdateSerializer(serializers.Serializer):
    id = serializers.CharField()
    text = serializers.CharField()
