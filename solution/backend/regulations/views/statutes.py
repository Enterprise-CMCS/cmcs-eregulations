from rest_framework import serializers, viewsets

from regulations.models import StatuteLinkConverter


class StatuteLinkConverterSerializer(serializers.Serializer):
    section = serializers.CharField()
    title = serializers.IntegerField()
    usc = serializers.CharField()
    act = serializers.CharField()
    name = serializers.CharField()
    statute_title = serializers.CharField()
    source_url = serializers.CharField()


class StatuteLinkConverterViewSet(viewsets.ReadOnlyModelViewSet):
    model = StatuteLinkConverter
    serializer_class = StatuteLinkConverterSerializer

    def get_queryset(self):
        act = self.request.GET.get("act", None)
        queryset = self.model.objects
        return queryset.filter(act__iexact=act) if act else queryset.all()
