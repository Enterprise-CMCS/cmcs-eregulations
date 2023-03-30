from rest_framework import serializers


class SearchResultSerializer(serializers.Serializer):
    part_number = serializers.CharField()
    section_number = serializers.CharField()
    headline = serializers.CharField()
    parentHeadline = serializers.CharField()
    part_title = serializers.CharField()
    section_title = serializers.CharField()
    date = serializers.CharField()
    title = serializers.CharField()
