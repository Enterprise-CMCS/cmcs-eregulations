from drf_spectacular.utils import extend_schema
from rest_framework import serializers, viewsets

from common.api import OpenApiQueryParameter
from regulations.models import StatuteLinkConverter


class StatuteLinkConverterSerializer(serializers.Serializer):
    section = serializers.CharField()
    title = serializers.IntegerField()
    usc = serializers.CharField()
    act = serializers.CharField()
    name = serializers.CharField()
    statute_title = serializers.CharField()
    source_url = serializers.CharField()


@extend_schema(
    description="Retrieve a list of Statute Link Converters for a given act or all acts.",
    parameters=[OpenApiQueryParameter("act", "The act to filter down to.", str, False)],
)
class StatuteLinkConverterViewSet(viewsets.ReadOnlyModelViewSet):
    model = StatuteLinkConverter
    serializer_class = StatuteLinkConverterSerializer

    def get_queryset(self):
        act = self.request.GET.get("act", None)
        queryset = self.model.objects
        return queryset.filter(act__iexact=act) if act else queryset.all()
