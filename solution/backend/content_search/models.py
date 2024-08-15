
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
from django.db.models.signals import post_save
from django.dispatch import receiver

from common.constants import QUOTE_TYPES
from regcore.models import Part
from resources.models import (
    AbstractResource,
    FederalRegisterLink,
    InternalFile,
    InternalLink,
    PublicLink,
    ResourceContent,
)


class ContentIndexQuerySet(models.QuerySet):
    _text_max = int(settings.SEARCH_HEADLINE_TEXT_MAX)
    _min_words = int(settings.SEARCH_HEADLINE_MIN_WORDS)
    _max_words = int(settings.SEARCH_HEADLINE_MAX_WORDS)
    _max_fragments = int(settings.SEARCH_HEADLINE_MAX_FRAGMENTS) or None

    def _is_quoted(self, query):
        return query.startswith(QUOTE_TYPES) and query.endswith(QUOTE_TYPES)

    def _get_search_query_object(self, search_query):
        search_type = "phrase" if self._is_quoted(search_query) else "plain"
        return SearchQuery(search_query, search_type=search_type, config='english')

    def search(self, search_query):
        cover_density = self._is_quoted(search_query)
        rank_filter = float(settings.QUOTED_SEARCH_FILTER if cover_density else settings.BASIC_SEARCH_FILTER)
        return self.annotate(rank=SearchRank(
            RawSQL("vector_column", [], output_field=SearchVectorField()),
            self._get_search_query_object(search_query), cover_density=cover_density))\
            .filter(rank__gt=rank_filter)\
            .order_by('-rank')

    def generate_headlines(self, search_query):
        query_object = self._get_search_query_object(search_query)
        return self.annotate(content_short=Substr("content", 1, self._text_max)).annotate(
            summary_headline=SearchHeadline(
                "summary",
                query_object,
                start_sel="<span class='search-highlight'>",
                stop_sel='</span>',
                min_words=self._min_words,
                max_words=self._max_words,
                config='english',
                fragment_delimiter='...',
                max_fragments=self._max_fragments,
            ),
            name_headline=SearchHeadline(
                "name",
                query_object,
                start_sel="<span class='search-highlight'>",
                stop_sel="</span>",
                min_words=self._min_words,
                max_words=self._max_words,
                config='english',
                highlight_all=True,
                fragment_delimiter='...',
                max_fragments=self._max_fragments,
            ),
            content_headline=SearchHeadline(
                "content_short",
                query_object,
                start_sel="<span class='search-highlight'>",
                stop_sel="</span>",
                config='english',
                min_words=self._min_words,
                max_words=self._max_words,
                fragment_delimiter='...',
                max_fragments=self._max_fragments,
            ),
        )


class ContentIndexManager(models.Manager.from_queryset(ContentIndexQuerySet)):
    pass


class IndexedRegulationText(models.Model):
    # TODO: add fields for indexed reg text. see regcore/search/models.py.
    parent = models.ForeignKey(Part, on_delete=models.CASCADE)


# This model is an all encompassing searchable index allowing different models to share an index.
# Instead of recalculating the vector column each time a change in weights are done the values will be stored
# in the rank_{}_string fields.
class ContentIndex(models.Model):
    # Fields used for generating search headlines
    name = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    content = models.TextField(blank=True)

    # Rank fields for searching
    rank_a_string = models.TextField(blank=True)
    rank_b_string = models.TextField(blank=True)
    rank_c_string = models.TextField(blank=True)
    rank_d_string = models.TextField(blank=True)

    # OneToOne fields linked to possible indexed types
    resource = models.OneToOneField(AbstractResource, blank=True, null=True, on_delete=models.CASCADE, related_name="index")
    reg_text = models.OneToOneField(IndexedRegulationText, blank=True, null=True, on_delete=models.CASCADE, related_name="index")

    objects = ContentIndexManager()

    class Meta:
        verbose_name = "Content Index"
        verbose_name_plural = "Content Indices"


@receiver(post_save, sender=ResourceContent)
def update_content_field(sender, instance, created, **kwargs):
    index, _ = ContentIndex.objects.get_or_create(resource=instance.resource)
    index.content = instance.value
    index.save()


@receiver(post_save, sender=PublicLink)
@receiver(post_save, sender=FederalRegisterLink)
def update_indexed_public_resource(sender, instance, created, **kwargs):
    index, _ = ContentIndex.objects.get_or_create(resource=instance)
    index.name = instance.document_id
    index.summary = instance.title
    index.rank_a_string = "{} {}".format(
        instance.document_id,
        instance.title,
    )
    index.rank_b_string = ""
    index.rank_c_string = instance.date
    index.rank_d_string = " ".join([str(i) for i in instance.subjects.all()])
    index.save()


@receiver(post_save, sender=InternalFile)
def update_indexed_internal_file(sender, instance, created, **kwargs):
    index, _ = ContentIndex.objects.get_or_create(resource=instance)
    index.name = instance.title
    index.summary = instance.summary
    index.rank_a_string = instance.title
    index.rank_b_string = instance.summary
    index.rank_c_string = "{} {}".format(
        instance.date,
        instance.file_name,
    )
    index.rank_d_string = " ".join([str(i) for i in instance.subjects.all()])
    index.save()


@receiver(post_save, sender=InternalLink)
def update_indexed_internal_link(sender, instance, created, **kwargs):
    index, _ = ContentIndex.objects.get_or_create(resource=instance)
    index.name = instance.title
    index.summary = instance.summary
    index.rank_a_string = instance.title
    index.rank_b_string = instance.summary
    index.rank_c_string = instance.date
    index.rank_d_string = " ".join([str(i) for i in instance.subjects.all()])
    index.save()


@receiver(post_save, sender=Part)
def update_indexed_part(sender, instance, created, **kwargs):
    pass
