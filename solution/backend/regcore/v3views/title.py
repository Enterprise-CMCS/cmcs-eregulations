from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema

from .utils import OpenApiPathParameter
from .mixins import MultipleFieldLookupMixin
from regcore.models import Part
from regcore.views import SettingsAuthentication

from regcore.serializers.toc import (
    TOCSerializer,
    FrontPageTOCSerializer,
    TitleTOCSerializer,
)
from regcore.serializers.metadata import PartsSerializer

from regcore.serializers.metadata import StringListSerializer


@extend_schema(description="Retrieve the table of contents (TOC) for all Titles, with detail down to the Part level. "
                           "Each object in the array is a TOC for a specific Title.")
class ContentsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Part.objects.order_by("title", "name", "-date").distinct("title", "name").values_list("depth_stack", flat=True)
    serializer_class = FrontPageTOCSerializer


@extend_schema(description="Retrieve a simple list of all Titles in the system.")
class TitlesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Part.objects.order_by("title").distinct("title").values_list("title", flat=True)
    serializer_class = StringListSerializer


@extend_schema(
    description="Retrieve the table of contents for a specific Title, with detail down to the Part level.",
    parameters=[OpenApiPathParameter("title", "Title of interest, e.g. 42.", int)],
)
class TitleContentsViewSet(MultipleFieldLookupMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = TitleTOCSerializer
    
    def get_queryset(self):
        title = self.kwargs.get("title")
        return Part.objects.filter(title=title).order_by("title", "name", "-date").distinct("title", "name").values_list("depth_stack", flat=True)


@extend_schema(
    description="Retrieve a list of the latest version of each Part contained within a specific Title, in numerical order.",
    parameters=[OpenApiPathParameter("title", "Title to retrieve Parts from, e.g. 42.", int)],
)
class PartsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PartsSerializer

    def get_queryset(self):
        title = self.kwargs.get("title")
        return Part.objects.filter(title=title).order_by("name", "-date").distinct("name")
