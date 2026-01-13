from rest_framework import serializers


class HistorySerializer(serializers.Serializer):
    year = serializers.CharField()
    link = serializers.CharField()


class EcfrHistorySerializer(serializers.Serializer):
    version = serializers.CharField()
    version_link = serializers.CharField()
    compare_to_previous_link = serializers.CharField()
    compare_to_current_link = serializers.CharField()
