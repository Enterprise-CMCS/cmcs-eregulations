from datetime import date

from rest_framework import generics, serializers
from django.db import models

from regcore.models import Part
from .models import Part, SearchIndex
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchHeadline

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError


class SearchViewSerializer(serializers.ModelSerializer):
    headline = serializers.CharField()
    regulation_title = serializers.CharField(source="part__document__title")
    title = serializers.CharField(source="part__title")
    date = serializers.DateField(source="part__date")

    class Meta:
        model = SearchIndex
        fields = ("type", "content", "headline", "label", "parent", "regulation_title", "title", "date")


class SearchView(generics.ListAPIView):
    serializer_class = SearchViewSerializer

    def get_queryset(self):
        q = self.request.query_params.get("q")
        return SearchIndex.objects\
            .filter(part__in=models.Subquery(Part.objects.effective(date.today()).values("id")))\
            .filter(search_vector=SearchQuery(q))\
            .annotate(rank=SearchRank("search_vector", SearchQuery(q)))\
            .annotate(
                headline=SearchHeadline(
                    "content",
                    SearchQuery(q),
                    start_sel='<span class="search-highlight">',
                    stop_sel='</span>',
                ),
            )\
            .order_by('-rank')\
            .values("type", "content", "headline", "label", "parent", "part__document__title", "part__title", "part__date")
