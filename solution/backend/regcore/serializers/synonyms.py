from rest_framework import serializers


class SynonymSerializer(serializers.Serializer):
    baseWord = serializers.CharField()
    isActive = serializers.BooleanField()


class SynonymsSerializer(serializers.Serializer):
    isActive = serializers.BooleanField()
    baseWord = serializers.CharField()
    synonyms = SynonymSerializer(read_only=True, many=True)
