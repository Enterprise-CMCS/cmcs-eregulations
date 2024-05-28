from django.db.models import Prefetch
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from drf_spectacular.utils import extend_schema

from resources.serializers import (
    AbstractCitationSerializer,
    PublicCategorySerializer,
    MetaCategorySerializer,
    SubpartWithChildrenSerializer,
    SectionWithParentSerializer,
)

from resources.models import (
    AbstractCitation,
    NewSection,
    NewSubpart,
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
