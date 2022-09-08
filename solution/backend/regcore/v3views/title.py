from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema

from .utils import OpenApiPathParameter
from .mixins import MultipleFieldLookupMixin
from regcore.models import Title, Part
from regcore.views import SettingsAuthentication

from regcore.serializers.toc import TOCSerializer
from regcore.serializers.metadata import (
    TitlesSerializer,
    TitleRetrieveSerializer,
    PartsSerializer,
)


@extend_schema(description="Retrieve the table of contents (TOC) for all Titles, with detail down to the Part level. "
                           "Each object in the array is a TOC for a specific Title.")
class ContentsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Title.objects.all().values_list("toc", flat=True)
    serializer_class = TOCSerializer


@extend_schema(description="Retrieve a simple list of all Titles in the system.")
class TitlesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitlesSerializer


@extend_schema(
    description="Retrieve, create, or update a specific Title object.",
    parameters=[OpenApiPathParameter("title", "Title of interest, e.g. 42.", int)],
)
class TitleViewSet(MultipleFieldLookupMixin, viewsets.ModelViewSet):
    queryset = Title.objects.all()
    lookup_fields = {"name": "title"}

    authentication_classes = [SettingsAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        # TODO: REWRITE THIS VIEWSET
        #if self.request.method == "POST" or self.request.method == "PUT":
        #    return TitleUploadSerializer
        return TitleRetrieveSerializer


@extend_schema(
    description="Retrieve the table of contents for a specific Title, with detail down to the Part level.",
    parameters=[OpenApiPathParameter("title", "Title of interest, e.g. 42.", int)],
)
class TitleContentsViewSet(MultipleFieldLookupMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Title.objects.all().values_list("toc", flat=True)
    serializer_class = TOCSerializer
    lookup_fields = {"name": "title"}


@extend_schema(
    description="Retrieve a list of the latest version of each Part contained within a specific Title, in numerical order.",
    parameters=[OpenApiPathParameter("title", "Title to retrieve Parts from, e.g. 42.", int)],
)
class PartsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PartsSerializer

    def get_queryset(self):
        title = self.kwargs.get("title")
        return Part.objects.filter(title=title).order_by("name", "-date").distinct("name")
