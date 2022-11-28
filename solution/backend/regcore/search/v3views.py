from datetime import date
from rest_framework import viewsets

from .models import SearchIndex
from .serializers import SearchResultSerializer

from common.mixins import OptionalPaginationMixin


class V3SearchView(OptionalPaginationMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = SearchResultSerializer

    def get_queryset(self):
        query = self.request.GET.get("q")
        return SearchIndex.objects.effective(date.today()).search(query)
