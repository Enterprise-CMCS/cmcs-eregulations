from rest_framework import serializers


class SubjectSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    short_name = serializers.CharField()
    abbreviation = serializers.CharField()
    description = serializers.CharField()
    public_resources = serializers.IntegerField()
    internal_resources = serializers.IntegerField()
