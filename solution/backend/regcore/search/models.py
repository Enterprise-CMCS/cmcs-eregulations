
from django.contrib.postgres.search import (
    SearchHeadline,
    SearchQuery,
    SearchRank,
    SearchVectorField,
)
from django.db import models
from django.db.models.expressions import RawSQL

from common.constants import QUOTE_TYPES
from regcore.models import Part


class SearchIndexQuerySet(models.QuerySet):
    search_type = "plain"
    cover_density = False
    rank_filter = .2

    def effective(self, date):
        return self.filter(part__in=models.Subquery(Part.objects.effective(date.today()).values("id")))

    def search_configuration(self, query):

        if query and query.startswith(QUOTE_TYPES) and query.endswith(QUOTE_TYPES):
            self.search_type = "phrase"
            self.cover_density = True
            self.rank_filter = 0.01

    def search(self, query):
        self.search_configuration(query)

        search_query = SearchQuery(query, search_type=self.search_type, config='english')
        return self.annotate(rank=SearchRank(
            RawSQL("vector_column", [], output_field=SearchVectorField()),
            search_query, cover_density=self.cover_density))\
            .filter(rank__gt=self.rank_filter)\
            .annotate(headline=SearchHeadline(
                "content",
                search_query,
                start_sel='<span class="search-highlight">',
                stop_sel='</span>',
                config='english'
            ),
            parentHeadline=SearchHeadline(
                "section_title",
                search_query,
                start_sel="<span class='search-highlight'>",
                stop_sel="</span>",
                config='english',
                highlight_all=True
            ),
        ).order_by('-rank').prefetch_related('part')


class SearchIndexManager(models.Manager.from_queryset(SearchIndexQuerySet)):
    pass


class SearchIndexV2(models.Model):
    part_number = models.CharField(max_length=32)
    section_number = models.CharField(max_length=32)
    content = models.TextField()
    section_string = models.CharField(max_length=255)
    section_title = models.TextField(null=True)
    part_title = models.TextField(null=True)
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    objects = SearchIndexManager()


class Synonym(models.Model):
    isActive = models.BooleanField(default=True)
    baseWord = models.CharField(max_length=128)
    synonyms = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return self.baseWord if self.isActive else f'{self.baseWord} (inactive)'

    @property
    def filtered_synonyms(self):
        return self.synonyms.filter(isActive=True).order_by("baseWord")
