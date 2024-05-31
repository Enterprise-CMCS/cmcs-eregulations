from django.db.models import Prefetch
from rest_framework import viewsets

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
    serializer_class = AbstractCitationSerializer
    queryset = AbstractCitation.objects.select_subclasses()


class SectionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SectionWithParentSerializer
    queryset = Section.objects.prefetch_related(
        Prefetch("parent", Subpart.objects.all()),
    )


class SubpartViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubpartWithChildrenSerializer
    queryset = Subpart.objects.prefetch_related(
        Prefetch("children", Section.objects.all()),
    )
