from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema
from django.db.models import Prefetch

from .mixins import LocationExplorerViewSetMixin

from resources.models import (
    AbstractLocation,
    Section,
    Subpart,
)

from resources.v3serializers.locations import (
    AbstractLocationPolymorphicSerializer,
    FullSectionSerializer,
    FullSubpartSerializer,
    MetaLocationSerializer,
)

from regcore.views import SettingsAuthentication


@extend_schema(
    description="Retrieve a list of all resource locations, filterable by title and part. Results are paginated by default.",
    parameters=LocationExplorerViewSetMixin.PARAMETERS,
    responses=MetaLocationSerializer.many(True),
)
class LocationViewSet(LocationExplorerViewSetMixin, viewsets.ModelViewSet):
    queryset = AbstractLocation.objects.all().select_subclasses()
    serializer_class = AbstractLocationPolymorphicSerializer

    authentication_classes = [SettingsAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]


@extend_schema(
    description="Retrieve a list of all Section objects, filterable by title and part. Results are paginated by default.",
    parameters=LocationExplorerViewSetMixin.PARAMETERS,
)
class SectionViewSet(LocationExplorerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = FullSectionSerializer
    queryset = Section.objects.all().prefetch_related(
        Prefetch("parent", AbstractLocation.objects.all().select_subclasses()),
    )


@extend_schema(
    description="Retrieve a list of all Subpart objects, filterable by title and part. Results are paginated by default.",
    parameters=LocationExplorerViewSetMixin.PARAMETERS,
)
class SubpartViewSet(LocationExplorerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = FullSubpartSerializer
    queryset = Subpart.objects.all().prefetch_related(
        Prefetch("children", Section.objects.all()),
    )
