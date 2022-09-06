from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .utils import OpenApiPathParameter

from .mixins import (
    PartPropertiesViewSet,
    NodeFinderViewSet,
)

from regcore.part_serializers import (
    V3PartSerializer,
    SectionSerializer,
    SubpartSerializer,
)


@extend_schema(
    description="Retrieve the full textual contents and structure of a regulation Part. "
                "Note that children of a Part object will vary with object type. "
)
class PartViewSet(PartPropertiesViewSet):
    serializer_class = V3PartSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_object().document)
        return Response(serializer.data)


@extend_schema(
    description="Retrieve the full textual contents and structure of a section within a regulation's Part. "
                "Note that children of a Section object will vary with object type. ",
    parameters=[OpenApiPathParameter("section", "Section number to retrieve.", int)],
)
class SectionViewSet(NodeFinderViewSet):
    serializer_class = SectionSerializer
    parameter = "section"
    node_type = "SECTION"
    label_index = 1


@extend_schema(
    description="Retrieve the full textual contents and structure of a subpart within a regulation's Part. "
                "Note that children of a Subpart object will vary with object type. ",
    parameters=[OpenApiPathParameter("subpart", "Subpart to retrieve, e.g. A.", str)],
)
class SubpartViewSet(NodeFinderViewSet):
    serializer_class = SubpartSerializer
    parameter = "subpart"
    node_type = "SUBPART"
    label_index = 0
