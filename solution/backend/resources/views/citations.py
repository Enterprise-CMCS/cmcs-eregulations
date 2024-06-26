from django.db.models import Prefetch
from rest_framework import viewsets

from common.mixins import ViewSetPagination
from resources.models import (
    AbstractCitation,
    Section,
    Subpart,
)
from resources.serializers import (
    AbstractCitationSerializer,
    SectionWithParentSerializer,
    SubpartWithChildrenSerializer,
)


class CitationViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = ViewSetPagination
    serializer_class = AbstractCitationSerializer
    queryset = AbstractCitation.objects.select_subclasses()


class SectionViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = ViewSetPagination
    serializer_class = SectionWithParentSerializer
    queryset = Section.objects.prefetch_related(
        Prefetch("parent", Subpart.objects.all()),
    )


class SubpartViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = ViewSetPagination
    serializer_class = SubpartWithChildrenSerializer
    queryset = Subpart.objects.prefetch_related(
        Prefetch("children", Section.objects.all()),
    )
