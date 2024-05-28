from django.db.models import Prefetch
from rest_framework import viewsets

from resources.models import (
    AbstractCitation,
    NewSection,
    NewSubpart,
)
from resources.serializers import (
    AbstractCitationSerializer,
    SectionWithParentSerializer,
    SubpartWithChildrenSerializer,
)


class CitationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AbstractCitationSerializer
    queryset = AbstractCitation.objects.select_subclasses()


class SectionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SectionWithParentSerializer
    queryset = NewSection.objects.prefetch_related(
        Prefetch("parent", NewSubpart.objects.all()),
    )


class SubpartViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubpartWithChildrenSerializer
    queryset = NewSubpart.objects.prefetch_related(
        Prefetch("children", NewSection.objects.all()),
    )
