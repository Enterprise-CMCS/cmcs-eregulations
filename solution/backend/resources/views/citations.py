from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from cmcs_regulations.utils import ViewSetPagination
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
    description="Retrieve a list of legal citations, which may include references to sections, subparts, and other "
                "regulatory text. This endpoint supports access to different types of citations, and the results are "
                "ordered based on the specific citation subclass. "
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
