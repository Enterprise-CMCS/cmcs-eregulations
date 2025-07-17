from rest_framework import serializers


class ContentUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    text = serializers.CharField(required=False)
    file_type = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
