from datetime import date
from rest_framework import generics, serializers, viewsets
from django.db import models
from django.contrib.postgres.search import SearchHeadline, SearchQuery, SearchVector, SearchRank
from drf_spectacular.utils import extend_schema, OpenApiParameter

from regcore.models import Part
from .models import SearchIndex

from supplemental_content.models import AbstractSupplementalContent
from supplemental_content.serializers import FlatSupplementalContentSerializer


class SearchViewSerializer(serializers.ModelSerializer):
    headline = serializers.CharField()
    regulation_title = serializers.CharField(source="part__document__title")
    title = serializers.CharField(source="part__title")
    date = serializers.DateField(source="part__date")

    class Meta:
        model = SearchIndex
        fields = ("type", "content", "headline", "label", "parent", "regulation_title", "title", "date")


@extend_schema(
        parameters=[
          OpenApiParameter("q", str, OpenApiParameter.QUERY), ],
    )
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
                parentHeadline=SearchHeadline(
                    "parent__title",
                    SearchQuery(q),
                    start_sel="<span class='search-highlight'>",
                    stop_sel='</span>',
                ),
            )\
            .order_by('-rank')\
            .values("type", "content", "headline", "label", "parent", "part__document__title", "part__title", "part__date")


class SupplementalContentSearchViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FlatSupplementalContentSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q')
        search_type = 'plain'
        cover_density = False
        if (query.startswith('"')) and query.endswith('"'):
            search_type = 'phrase'
            cover_density = True

        return AbstractSupplementalContent.objects.filter(approved=True).annotate(rank=SearchRank(
                SearchVector('supplementalcontent__name', weight='A', config='english')
                + SearchVector('supplementalcontent__description', weight='A', config='english'),
                SearchQuery(query, search_type=search_type, config='english'), cover_density=cover_density))\
            .filter(rank__gte=0.2) \
            .annotate(
                nameHeadline=SearchHeadline(
                    "supplementalcontent__name",
                    SearchQuery(query, search_type=search_type, config='english'),
                    start_sel='<span class="search-highlight">',
                    stop_sel='</span>',
                    config='english'
                ),
                descriptionHeadline=SearchHeadline(
                    "supplementalcontent__description",
                    SearchQuery(query, search_type=search_type, config='english'),
                    start_sel='<span class="search-highlight">',
                    stop_sel='</span>',
                    config='english'
                )
            )\
            .order_by('-rank') \
            .prefetch_related('locations')\
            .prefetch_related('category').select_subclasses("supplementalcontent")
