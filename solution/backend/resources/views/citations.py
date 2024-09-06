from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
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


@extend_schema(
    description="Retrieve a list of regulation (CFR) citations. "
                "This endpoint provides access to multiple types of "
                "citations (section citations and subpart citations), "
                "and the results are in alphanumeric order based on citation "
                "hierarchy (title, part, subpart, and section)."
)
class CitationViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = ViewSetPagination
    serializer_class = AbstractCitationSerializer
    queryset = AbstractCitation.objects.select_subclasses()


@extend_schema(
    description="Retrieve a list of sections within regulatory text, including their parent subparts. "
                "This endpoint provides access to sections and their associated subparts, with the data "
                "prefetched and ordered according to their hierarchy."
)
class SectionViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = ViewSetPagination
    serializer_class = SectionWithParentSerializer
    queryset = Section.objects.prefetch_related(
        Prefetch("parent", Subpart.objects.all()),
    )


@extend_schema(
    description="Retrieve a list of subparts within regulatory text, including their child sections. "
                "This endpoint allows access to subparts and their associated sections, with data "
                "prefetched to include child sections and ordered by their hierarchical structure."
)
class SubpartViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = ViewSetPagination
    serializer_class = SubpartWithChildrenSerializer
    queryset = Subpart.objects.prefetch_related(
        Prefetch("children", Section.objects.all()),
    )
