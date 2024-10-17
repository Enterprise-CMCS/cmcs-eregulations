from rest_framework import serializers

from common.fields import HeadlineField
from resources.serializers import AbstractResourceSerializer


class IndexedRegulationTextSerializer(serializers.Serializer):
    title = serializers.IntegerField()
    date = serializers.CharField()
    part_title = serializers.CharField()
    part_number = serializers.IntegerField()
    node_type = serializers.CharField()
    node_id = serializers.CharField()
    node_title = serializers.CharField()


class ContentSearchSerializer(serializers.Serializer):
    name_headline = HeadlineField()
    summary_headline = HeadlineField()
    content_headline = HeadlineField(blank_when_no_highlight=True)

    resource = AbstractResourceSerializer()
    reg_text = IndexedRegulationTextSerializer()


class SubjectCountSerializer(serializers.Serializer):
    subject = serializers.IntegerField()
    count = serializers.IntegerField()


class CategoryCountSerializer(serializers.Serializer):
    category = serializers.IntegerField()
    parent = serializers.IntegerField()
    count = serializers.IntegerField()


class ContentCountSerializer(serializers.Serializer):
    internal_resource_count = serializers.IntegerField()
    public_resource_count = serializers.IntegerField()
    regulation_text_count = serializers.IntegerField()

    subjects = SubjectCountSerializer(many=True)
    categories = CategoryCountSerializer(many=True)
