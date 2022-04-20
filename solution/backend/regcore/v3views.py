from django.shortcuts import get_object_or_404
from django.http import Http404

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema, OpenApiParameter

from regcore.models import Title, Part, ParserResult
from regcore.views import SettingsAuthentication

from regcore.serializers import (
    FlatContentsSerializer,
    ContentsSerializer,
    TitlesSerializer,
    TitleRetrieveSerializer,
    TitleUploadSerializer,
    PartsSerializer,
    VersionsSerializer,
    ParserResultSerializer
)


def OpenApiPathParameter(name, description, type):
    return OpenApiParameter(name=name, description=description, required=True, type=type, location=OpenApiParameter.PATH)


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


@extend_schema(description="Retrieve the table of contents (TOC) for all Titles, with detail down to the Part level. "
                           "Each object in the array is a TOC for a specific Title.")
class ContentsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Title.objects.all().values_list("toc", flat=True)
    serializer_class = ContentsSerializer


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
        if self.request.method == "POST" or self.request.method == "PUT":
            return TitleUploadSerializer
        return TitleRetrieveSerializer


@extend_schema(
    description="Retrieve the table of contents for a specific Title, with detail down to the Part level.",
    parameters=[OpenApiPathParameter("title", "Title of interest, e.g. 42.", int)],
)
class TitleContentsViewSet(MultipleFieldLookupMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Title.objects.all().values_list("toc", flat=True)
    serializer_class = ContentsSerializer
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


@extend_schema(
    description="Retrieve a list of versions of a specific Part within a specific Title. Response is a simple list of strings.",
    parameters=[
        OpenApiPathParameter("title", "Title where Part is contained, e.g. 42.", int),
        OpenApiPathParameter("part", "Part of interest, e.g. 433.", int),
    ],
    responses={(200, "application/json"): {"type": "string"}},
)
class VersionsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VersionsSerializer

    def get_queryset(self):
        title = self.kwargs.get("title")
        part = self.kwargs.get("part")
        return Part.objects.filter(title=title, name=part).order_by("-date").values_list("date", flat=True)


# Inherit from this class to retrieve attributes from a specific version of a part
# You must specify a serializer_class
@extend_schema(
    parameters=[
        OpenApiPathParameter("title", "Title where Part is contained, e.g. 42.", int),
        OpenApiPathParameter("part", "Part of interest, e.g. 433.", int),
        OpenApiPathParameter("version", "Version of the Part. Must be in YYYY-MM-DD format (e.g. 2021-01-31), "
                             "or \"latest\" to retrieve the most recent version.", str),
    ],
)
class PartPropertiesViewSet(MultipleFieldLookupMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Part.objects.all()
    lookup_fields = {
        "title": "title",
        "name": "part",
        "date": "version",
    }


@extend_schema(description="Retrieve the table of contents for a specific version of a specific Part of a specific Title, "
                           "with detail down to the Section level.")
class PartContentsViewSet(PartPropertiesViewSet):
    serializer_class = ContentsSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_object().toc)
        return Response(serializer.data)


# Inherit from this class to retrieve a flat list of specific types of nodes within a part's structure
# You must specify a node_type
class PartStructureNodesViewSet(PartPropertiesViewSet):
    serializer_class = FlatContentsSerializer

    def find_nodes(self, structure):
        nodes = []
        for child in structure["children"]:
            if child["type"] == self.node_type:
                nodes.append(child)
            if child["children"]:
                nodes = nodes + self.find_nodes(child)
        return nodes

    def retrieve(self, request, *args, **kwargs):
        nodes = self.find_nodes(self.get_object().toc)
        return Response(self.serializer_class(nodes, many=True).data)


@extend_schema(description="Retrieve a list of Sections contained within a version of a Part.")
class PartSectionsViewSet(PartStructureNodesViewSet):
    node_type = "section"


@extend_schema(description="Retrieve a list of Subparts contained within a version of a Part.")
class PartSubpartsViewSet(PartStructureNodesViewSet):
    node_type = "subpart"


@extend_schema(
    description="Retrieve a table of contents for a specific Subpart contained within a Part, "
                "with detail down to the Section level.",
    parameters=[OpenApiPathParameter("subpart", "The Subpart of interest, e.g. A.", str)],
)
class SubpartContentsViewSet(PartPropertiesViewSet):
    serializer_class = ContentsSerializer

    def retrieve(self, request, *args, **kwargs):
        for node in self.get_object().toc["children"]:
            if node["type"] == "subpart" and len(node["identifier"]) and node["identifier"][0] == self.kwargs.get("subpart"):
                return Response(self.serializer_class(node["children"], many=True).data)
        raise Http404()

@extend_schema(
    description="Retrieve the latest ParserResult or create a new ParserResult object for the title.",
    parameters=[OpenApiPathParameter("title", "Title the parser was run for, e.g. 42.", int)],
)
class ParserResultViewSet(viewsets.ModelViewSet):
    serializer_class = ParserResultSerializer
    authentication_classes = [SettingsAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def retrieve(self, request, title):
        parserResult = ParserResult.objects.filter(title=title).order_by("-end").first()
        if parserResult:
            serializer = self.serializer_class(parserResult)
            return Response(serializer.data)
        raise Http404()
