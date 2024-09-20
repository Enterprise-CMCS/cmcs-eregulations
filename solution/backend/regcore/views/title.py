from django.contrib.postgres.aggregates import ArrayAgg
from django.db import models
from django.db.models.functions import Cast
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from regcore.models import Part
from regcore.serializers.metadata import PartsSerializer, StringListSerializer, VersionsSerializer
from regcore.serializers.toc import (
    FrontPageTOCSerializer,
    TitleTOCSerializer,
)

from .utils import OpenApiPathParameter


@extend_schema(
    tags=["regcore/metadata"],
    description="Retrieve the table of contents (TOC) for all Titles, with detail down to the Part level. "
                "Each object in the array is a TOC for a specific Title.",
)
class TOCViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Part.objects.order_by("title", "name", "-date").distinct("title", "name").values_list("depth_stack", flat=True)
    serializer_class = FrontPageTOCSerializer


@extend_schema(
    tags=["regcore/metadata"],
    description="Retrieve a simple list of all Titles in the system.",
    responses={(200, "application/json"): {"type": "string"}},
)
class TitlesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Part.objects.order_by("title").distinct("title").values_list("title", flat=True)
    serializer_class = StringListSerializer


@extend_schema(
    tags=["regcore/metadata"],
    description="Retrieve the table of contents for a specific Title, with detail down to the Part level.",
    parameters=[OpenApiPathParameter("title", "Title of interest, e.g. 42.", int)],
)
class TitleTOCViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TitleTOCSerializer

    def get_queryset(self):
        title = self.kwargs.get("title")
        return Part.objects.filter(title=title).order_by("title", "name", "-date")\
                   .distinct("title", "name").values_list("depth_stack", flat=True)

    def retrieve(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema(
    tags=["regcore/metadata"],
    description="Retrieve a list of the latest version of each Part contained within a specific Title, in numerical order.",
    parameters=[OpenApiPathParameter("title", "Title to retrieve Parts from, e.g. 42.", int)],
)
class PartsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PartsSerializer

    def get_queryset(self):
        title = self.kwargs.get("title")
        return Part.objects.filter(title=title).order_by("name", "-date").distinct("name")


@extend_schema(
    tags=["regcore/metadata"],
    description="Retrieve a list of parts associated with each version of the regulations.",
    parameters=[OpenApiPathParameter("title", "Title to retrieve versions from, e.g. 42.", int)],
)
class VersionsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VersionsSerializer

    def get_queryset(self):
        title = self.kwargs.get("title")
        return Part.objects.filter(title=title).values('date').annotate(
            part_name=ArrayAgg(Cast('name', models.CharField()), delimiter=','),
        )
