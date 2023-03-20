from rest_framework import serializers


class SearchResultSerializer(serializers.Serializer):
    part_number = serializers.CharField()
    section_number = serializers.CharField()
    rank = serializers.FloatField()
    headline = serializers.CharField()
    parentHeadline = serializers.CharField()
    part_title = serializers.IntegerField()
    part_document_title = serializers.CharField()
    date = serializers.CharField()
