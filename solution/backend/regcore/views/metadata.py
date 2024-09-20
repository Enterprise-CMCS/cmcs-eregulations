from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.response import Response

from regcore.serializers.toc import TOCSerializer

from .mixins import (
    PartPropertiesMixin,
    PartStructureNodesMixin,
)
from .utils import OpenApiPathParameter


@extend_schema(
    tags=["regcore/metadata"],
    description="Retrieve the table of contents for a specific version of a specific Part of a specific Title, "
                "with detail down to the Section level.",
    parameters=PartPropertiesMixin.PARAMETERS,
)
class PartTOCViewSet(PartPropertiesMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = TOCSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_object().toc)
        return Response(serializer.data)


@extend_schema(
    tags=["regcore/metadata"],
    description="Retrieve a list of Sections contained within a version of a Part.",
    parameters=PartStructureNodesMixin.PARAMETERS,
)
class PartSectionsViewSet(PartStructureNodesMixin, viewsets.ReadOnlyModelViewSet):
    node_type = "section"


@extend_schema(
    tags=["regcore/metadata"],
    description="Retrieve a list of Subparts contained within a version of a Part.",
    parameters=PartStructureNodesMixin.PARAMETERS,
)
class PartSubpartsViewSet(PartStructureNodesMixin, viewsets.ReadOnlyModelViewSet):
    node_type = "subpart"


@extend_schema(
    tags=["regcore/metadata"],
    description="Retrieve a table of contents for a specific Subpart contained within a Part, "
                "with detail down to the Section level.",
    parameters=[OpenApiPathParameter("subpart", "The Subpart of interest, e.g. A.", str)] + PartPropertiesMixin.PARAMETERS,
)
class SubpartTOCViewSet(PartPropertiesMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = TOCSerializer

    def retrieve(self, request, *args, **kwargs):
        for node in self.get_object().toc["children"]:
            if node["type"] == "subpart" and len(node["identifier"]) and node["identifier"][0] == self.kwargs.get("subpart"):
                return Response(self.serializer_class(node["children"], many=True).data)
        raise Http404()
