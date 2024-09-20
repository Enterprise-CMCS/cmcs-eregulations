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
    statute_title_roman = serializers.CharField()
    source_url = serializers.CharField()


@extend_schema(
    tags=["regulations/statutes"],
    description="Retrieve a list of Statute Link Converters for a given act or all acts.",
    parameters=[
        OpenApiQueryParameter("act", "The act to filter down to.", str, False),
        OpenApiQueryParameter("title", "The title to filter down to. Act must be specified for this.", str, False),
    ],
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
        return queryset.order_by("act", "statute_title", "usc_sort")


class ActListSerializer(serializers.Serializer):
    act = serializers.CharField()
    title = serializers.IntegerField(source="statute_title")
    title_roman = serializers.CharField(source="statute_title_roman")


@extend_schema(
    tags=["regulations/statutes"],
    description="Retrieve a list of all acts and their titles. Compiled from internal Statute Link Converters.",
)
class ActListViewSet(viewsets.ReadOnlyModelViewSet):
    model = StatuteLinkConverter
    serializer_class = ActListSerializer

    def get_queryset(self):
        return self.model.objects\
            .exclude(act__isnull=True)\
            .exclude(act__exact='')\
            .exclude(statute_title__isnull=True)\
            .order_by("act", "statute_title")\
            .distinct("act", "statute_title")
