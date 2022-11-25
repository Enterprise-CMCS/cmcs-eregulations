from datetime import date
from rest_framework import viewsets

from .models import SearchIndex
from .serializers import SearchResultSerializer

class V3SearchView(viewsets.ReadOnlyModelViewSet):
    serializer_class = SearchResultSerializer

    def get_queryset(self):
        query = self.request.GET.get("q")
        return SearchIndex.objects.effective(date.today()).search(query)
