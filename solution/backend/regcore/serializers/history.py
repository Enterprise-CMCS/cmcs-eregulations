from rest_framework import serializers


class HistorySerializer(serializers.Serializer):
    year = serializers.CharField()
    link = serializers.CharField()
