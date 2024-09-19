from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.response import Response

from regcore.serializers.contents import (
    PartSerializer,
    SectionContentsSerializer,
    SubpartContentsSerializer,
)

from .mixins import (
    NodeFinderMixin,
    PartPropertiesMixin,
)
from .utils import OpenApiPathParameter


@extend_schema(
    tags=["regcore/regtext"],
    description="Retrieve the full textual contents and structure of a regulation Part. "
                "Note that children of a Part object will vary with object type. ",
    parameters=PartPropertiesMixin.PARAMETERS,
)
class PartViewSet(PartPropertiesMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = PartSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_object().document)
        return Response(serializer.data)


@extend_schema(
    tags=["regcore/regtext"],
    description="Retrieve the full textual contents and structure of a section within a regulation's Part. "
                "Note that children of a Section object will vary with object type. ",
    parameters=[OpenApiPathParameter("section", "Section number to retrieve.", int)] + NodeFinderMixin.PARAMETERS,
)
class SectionViewSet(NodeFinderMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = SectionContentsSerializer
    parameter = "section"
    node_type = "SECTION"
    label_index = 1


@extend_schema(
    tags=["regcore/regtext"],
    description="Retrieve the full textual contents and structure of a subpart within a regulation's Part. "
                "Note that children of a Subpart object will vary with object type. ",
    parameters=[OpenApiPathParameter("subpart", "Subpart to retrieve, e.g. A.", str)] + NodeFinderMixin.PARAMETERS,
)
class SubpartViewSet(NodeFinderMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = SubpartContentsSerializer
    parameter = "subpart"
    node_type = "SUBPART"
    label_index = 0
