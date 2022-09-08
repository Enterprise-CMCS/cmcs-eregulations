from rest_framework import viewsets
from drf_spectacular.utils import extend_schema

from .utils import OpenApiPathParameter

from regcore.serializers.metadata import StringListSerializer
from regcore.models import Part


@extend_schema(
    description="Retrieve a list of versions of a specific Part within a specific Title. Response is a simple list of strings.",
    parameters=[
        OpenApiPathParameter("title", "Title where Part is contained, e.g. 42.", int),
        OpenApiPathParameter("part", "Part of interest, e.g. 433.", int),
    ],
    responses={(200, "application/json"): {"type": "string"}},
)
class VersionsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StringListSerializer

    def get_queryset(self):
        title = self.kwargs.get("title")
        part = self.kwargs.get("part")
        return Part.objects.filter(title=title, name=part).order_by("-date").values_list("date", flat=True)
