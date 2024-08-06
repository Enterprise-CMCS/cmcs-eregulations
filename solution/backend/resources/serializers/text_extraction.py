from rest_framework import serializers


class ContentUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    text = serializers.CharField()
