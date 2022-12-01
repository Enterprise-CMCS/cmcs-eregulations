from datetime import date
from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from django.db.models import F

from common.mixins import OptionalPaginationMixin
from common.api import OpenApiQueryParameter

from .models import SearchIndex
from .serializers import SearchResultSerializer


@extend_schema(
    description="Search the regulation text. This endpoint is incomplete and may change. Results are paginated by default.",
    parameters=[OpenApiQueryParameter("q", "The word or phrase to search for.", str, True)] + OptionalPaginationMixin.PARAMETERS,
)
class V3SearchView(OptionalPaginationMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = SearchResultSerializer

    def get_queryset(self):
        query = self.request.GET.get("q")
        return SearchIndex.objects.effective(date.today()).search(query).annotate(
            part_title=F("part__title"),
            part_document_title=F("part__document__title"),
            date=F("part__date"),
        )
