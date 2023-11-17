import uuid

from django.contrib.postgres.search import (
    SearchHeadline,
    SearchQuery,
    SearchRank,
    SearchVectorField,
)
from django.db import models
from django.db.models.expressions import RawSQL

from common.constants import QUOTE_TYPES
from common.fields import VariableDateField
from file_manager.models import DocumentType, Subject, UploadedFile
from resources.models import AbstractCategory, AbstractLocation, FederalRegisterDocument, SupplementalContent


class ContentIndexQuerySet(models.QuerySet):
    search_type = "plain"
    cover_density = False
    rank_filter = .1

    def search_configuration(self, query):

        if query and query.startswith(QUOTE_TYPES) and query.endswith(QUOTE_TYPES):
            self.search_type = "phrase"
            self.cover_density = True
            self.rank_filter = 0.01

    def search(self, search_query):
        self.search_configuration(search_query)

        search_query = SearchQuery(search_query, search_type=self.search_type, config='english')

        return self.annotate(rank=SearchRank(
            RawSQL("vector_column", [], output_field=SearchVectorField()),
            search_query, cover_density=self.cover_density))\
            .filter(rank__gt=self.rank_filter)\
            .annotate(summary_headline=SearchHeadline(
                "summary_string",
                search_query,
                start_sel='<span class="search-highlight">',
                stop_sel='</span>',
                min_words=30,
                config='english',
                fragment_delimiter='...'
            ),
            document_name_headline=SearchHeadline(
                "doc_name_string",
                search_query,
                start_sel="<span class='search-highlight'>",
                stop_sel="</span>",
                config='english',
                min_words=30,
                highlight_all=True,
                fragment_delimiter='...'
            ),
            content_headline=SearchHeadline(
                "content",
                search_query,
                start_sel="<span class='search-highlight'>",
                stop_sel="</span>",
                config='english',
                min_words=30,
                fragment_delimiter='...'
            ),
        ).order_by('-rank')


class ContentIndexManager(models.Manager.from_queryset(ContentIndexQuerySet)):
    pass


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
    subjects = models.ManyToManyField(Subject, blank=True, related_name="content")
    document_type = models.ForeignKey(DocumentType, blank=True, null=True, related_name="content", on_delete=models.SET_NULL)
    category = models.ForeignKey(
        AbstractCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name="content"
    )
    locations = models.ManyToManyField(AbstractLocation, blank=True, related_name="content", verbose_name="Regulation Locations")
    resource_type = models.CharField(max_length=25, null=True, blank=True)
    # content_type = models.CharField(max_length=50, blank=True, null=True)
    # content_id = models.IntegerField(null=True)
    file = models.ForeignKey(UploadedFile, blank=True, null=True, on_delete=models.CASCADE)
    supplemental_content = models.ForeignKey(SupplementalContent, blank=True, null=True, on_delete=models.CASCADE)
    fr_doc = models.ForeignKey(FederalRegisterDocument, blank=True, null=True, on_delete=models.CASCADE)
    objects = ContentIndexManager()
