from rest_framework.response import Response
from django.http import Http404
from drf_spectacular.utils import extend_schema

from .utils import OpenApiPathParameter

from .mixins import (
    PartPropertiesViewSet,
    PartStructureNodesViewSet,
)

from regcore.serializers import ContentsSerializer


@extend_schema(description="Retrieve the table of contents for a specific version of a specific Part of a specific Title, "
                           "with detail down to the Section level.")
class PartContentsViewSet(PartPropertiesViewSet):
    serializer_class = ContentsSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_object().toc)
        return Response(serializer.data)


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
