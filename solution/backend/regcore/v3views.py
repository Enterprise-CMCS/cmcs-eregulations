from django.contrib.postgres.search import SearchHeadline, SearchQuery, SearchVector, SearchRank
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from regcore.models import Title, Part
from regcore.views import SettingsAuthentication

from regcore.serializers import (
    ContentsSerializer,
    TitlesSerializer,
    TitleSerializer,
    PartsSerialier,
    VersionsSerializer,
    PartSectionsSerializer,
    PartSubpartsSerializer,
    SubpartContentsSerializer,
)

from supplemental_content.models import AbstractSupplementalContent
from supplemental_content.serializers import FlatSupplementalContentSerializer


class MultipleFieldLookupMixin(object):
    # must define lookup_fields mapping with entries like { "field_name": "url_parameter", ... }
    def get_object(self):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        filter = {}
        latest_field = None
        for field, param in self.lookup_fields.items():
            value = self.kwargs.get(param, None)
            if param == "version" and value == "latest":
                latest_field = field
            elif value:
                filter[field] = value
        return queryset.filter(**filter).latest(latest_field) if latest_field else get_object_or_404(queryset, **filter)


class ContentsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Title.objects.all()
    serializer_class = ContentsSerializer


class TitlesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitlesSerializer


class TitleViewSet(MultipleFieldLookupMixin, viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    lookup_fields = {"name": "title"}

    authentication_classes = [SettingsAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]


class TitleContentsViewSet(MultipleFieldLookupMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Title.objects.all()
    serializer_class = ContentsSerializer
    lookup_fields = {"name": "title"}


class PartsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PartsSerialier

    def get_queryset(self):
        title = self.kwargs.get("title")
        return Part.objects.filter(title=title).order_by("name", "-date").distinct("name")


class VersionsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VersionsSerializer

    def get_queryset(self):
        title = self.kwargs.get("title")
        part = self.kwargs.get("part")
        return Part.objects.filter(title=title, name=part).order_by("-date")


# Inherit from this class to retrieve attributes from a specific version of a part
# You must specify a serializer_class
class PartPropertiesViewSet(MultipleFieldLookupMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Part.objects.all()
    lookup_fields = {
        "title": "title",
        "name": "part",
        "date": "version",
    }


class PartContentsViewSet(PartPropertiesViewSet):
    serializer_class = ContentsSerializer


class PartSectionsViewSet(PartPropertiesViewSet):
    serializer_class = PartSectionsSerializer


class PartSubpartsViewSet(PartPropertiesViewSet):
    serializer_class = PartSubpartsSerializer


class SubpartContentsViewSet(PartPropertiesViewSet):
    serializer_class = SubpartContentsSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["subpart"] = self.kwargs.get("subpart")
        return context

class SupplementalContentSearchViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FlatSupplementalContentSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q')
        search_type = 'plain'
        cover_density = False
        if (query.startswith('"')) and query.endswith('"'):
            search_type = 'phrase'
            cover_density = True

        return AbstractSupplementalContent.objects.filter(approved=True).annotate(rank=SearchRank(
                SearchVector('supplementalcontent__name', weight='A', config='english')
                + SearchVector('supplementalcontent__description', weight='A', config='english'),
                SearchQuery(query, search_type=search_type, config='english'), cover_density=cover_density))\
            .filter(rank__gte=0.2) \
            .annotate(
                nameHeadline=SearchHeadline(
                    "supplementalcontent__name",
                    SearchQuery(query, search_type=search_type, config='english'),
                    start_sel='<span class="search-highlight">',
                    stop_sel='</span>',
                    config='english'
                ),
                descriptionHeadline=SearchHeadline(
                    "supplementalcontent__description",
                    SearchQuery(query, search_type=search_type, config='english'),
                    start_sel='<span class="search-highlight">',
                    stop_sel='</span>',
                    config='english'
                )
            )\
            .order_by('-rank') \
            .prefetch_related('locations')\
            .prefetch_related('category').select_subclasses("supplementalcontent")

