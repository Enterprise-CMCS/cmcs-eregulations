from rest_framework import serializers


class SearchResultSerializer(serializers.Serializer):
    type = serializers.CharField()
    label = serializers.ListField(child=serializers.CharField())
    rank = serializers.FloatField()
    headline = serializers.CharField()
    parentHeadline = serializers.CharField()
    part_title = serializers.IntegerField()
    part_document_title = serializers.CharField()
    date = serializers.CharField()
