from drf_spectacular.utils import extend_schema
from rest_framework import serializers, viewsets
from rest_framework.exceptions import ValidationError

from common.api import OpenApiQueryParameter
from regulations.models import StatuteLinkConverter


class StatuteLinkConverterSerializer(serializers.Serializer):
    section = serializers.CharField()
    title = serializers.IntegerField()
    usc = serializers.CharField()
    act = serializers.CharField()
    name = serializers.CharField()
    statute_title = serializers.IntegerField()
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
        title = self.request.GET.get("title", None)
        if title and not act:
            raise ValidationError("You may specify either an act by itself, or an act and a title, but not a title by itself.")
        queryset = self.model.objects.all()
        if act:
            queryset = queryset.filter(act__iexact=act)
        if title:
            queryset = queryset.filter(statute_title__iexact=title)
        return queryset
