from rest_framework import serializers, viewsets

from regulations.models import StatuteLinkConverter


class StatuteLinkConverterSerializer(serializers.Serializer):
    section = serializers.CharField()
    title = serializers.IntegerField()
    usc = serializers.CharField()
    act = serializers.CharField()
    source_url = serializers.CharField()


class StatuteLinkConverterViewSet(viewsets.ReadOnlyModelViewSet):
    model = StatuteLinkConverter
    serializer_class = 
