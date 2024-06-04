from rest_framework import serializers

from common.fields import HeadlineField


class ContentListSerializer(serializers.Serializer):
    doc_name_string = serializers.CharField()
    file_name_string = serializers.CharField()
    date_string = serializers.DateField()
    summary_string = serializers.CharField()
    locations = serializers.SerializerMethodField()
    resource_type = serializers.CharField()
    # subjects = SubjectSerializer(many=True, read_only=True)
    category = serializers.SerializerMethodField()
    url = serializers.CharField()
    id = serializers.IntegerField()
    document_name_headline = HeadlineField()
    summary_headline = HeadlineField()
    # division = DivisionWithGroupSerializer()


class ContentSearchSerializer(ContentListSerializer, ):
    document_name_headline = HeadlineField()
    summary_headline = HeadlineField()
    content_headline = HeadlineField(blank_when_no_highlight=True)


class ContentUpdateSerializer(serializers.Serializer):
    id = serializers.CharField()
    text = serializers.CharField()
