import uuid

from django.conf import settings
from django.contrib.postgres.search import (
    SearchHeadline,
    SearchQuery,
    SearchRank,
    SearchVectorField,
)
from django.db import models
from django.db.models.expressions import RawSQL
from django.db.models.functions import Substr

from common.constants import QUOTE_TYPES
from common.fields import VariableDateField
from resources.models import NewAbstractResource


class ContentIndexQuerySet(models.QuerySet):
    text_max = int(settings.SEARCH_HEADLINE_TEXT_MAX)
    min_words = int(settings.SEARCH_HEADLINE_MIN_WORDS)
    max_words = int(settings.SEARCH_HEADLINE_MAX_WORDS)
    max_fragments = int(settings.SEARCH_HEADLINE_MAX_FRAGMENTS) or None

    def is_quoted(self, query):
        return query.startswith(QUOTE_TYPES) and query.endswith(QUOTE_TYPES)

    def get_search_query_object(self, search_query):
        search_type = "phrase" if self.is_quoted(search_query) else "plain"
        return SearchQuery(search_query, search_type=search_type, config='english')

    def search(self, search_query):
        cover_density = self.is_quoted(search_query)
        rank_filter = float(settings.QUOTED_SEARCH_FILTER if cover_density else settings.BASIC_SEARCH_FILTER)
        return self.annotate(rank=SearchRank(
            RawSQL("vector_column", [], output_field=SearchVectorField()),
            self.get_search_query_object(search_query), cover_density=cover_density))\
            .filter(rank__gt=rank_filter)\
            .order_by('-rank')

    def generate_headlines(self, search_query):
        query_object = self.get_search_query_object(search_query)
        return self.annotate(content_short=Substr("content", 1, self.text_max)).annotate(
            summary_headline=SearchHeadline(
                "summary_string",
                query_object,
                start_sel="<span class='search-highlight'>",
                stop_sel='</span>',
                min_words=self.min_words,
                max_words=self.max_words,
                config='english',
                fragment_delimiter='...',
                max_fragments=self.max_fragments,
            ),
            document_name_headline=SearchHeadline(
                "doc_name_string",
                query_object,
                start_sel="<span class='search-highlight'>",
                stop_sel="</span>",
                min_words=self.min_words,
                max_words=self.max_words,
                config='english',
                highlight_all=True,
                fragment_delimiter='...',
                max_fragments=self.max_fragments,
            ),
            content_headline=SearchHeadline(
                "content_short",
                query_object,
                start_sel="<span class='search-highlight'>",
                stop_sel="</span>",
                config='english',
                min_words=self.min_words,
                max_words=self.max_words,
                fragment_delimiter='...',
                max_fragments=self.max_fragments,
            ),
        )


class ContentIndexManager(models.Manager.from_queryset(ContentIndexQuerySet)):
    pass


# The index is supposed to be an all encompassing index allowing different models to share an index
# Instead of recalculating the vector column each time a change in weights are done the values will be stored
# in the field values of for the rank_{}_string.  This will allow simpler updates in the future.
class ContentIndex(models.Model):
    uid = models.CharField(
        primary_key=False,
        default=uuid.uuid4,
        editable=False,
        max_length=36)
    doc_name_string = models.CharField(max_length=512, null=True, blank=True)
    summary_string = models.TextField(blank=True, null=True)
    file_name_string = models.CharField(max_length=512, null=True, blank=True)
    date_string = VariableDateField()
    content = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=512, blank=True, null=True)
    extract_url = models.CharField(max_length=512, blank=True, null=True)
    ignore_robots_txt = models.BooleanField(default=False)
    resource_type = models.CharField(max_length=25, null=True, blank=True)
    rank_a_string = models.TextField(blank=True, null=True)
    rank_b_string = models.TextField(blank=True, null=True)
    rank_c_string = models.TextField(blank=True, null=True)
    rank_d_string = models.TextField(blank=True, null=True)
    resource = models.ForeignKey(NewAbstractResource, blank=True, null=True, on_delete=models.CASCADE)
    objects = ContentIndexManager()
