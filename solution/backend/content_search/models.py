
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
from resources.models import AbstractCategory, AbstractLocation, SupplementalContent


class ContentIndexQuerySet(models.QuerySet):
    search_type = "plain"
    cover_density = False
    rank_filter = .2

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
                config='english'
            ),
            document_name_headline=SearchHeadline(
                "doc_name_string",
                search_query,
                start_sel="<span class='search-highlight'>",
                stop_sel="</span>",
                config='english',
                highlight_all=True
            ),
        ).order_by('-rank')


class ContentIndexManager(models.Manager.from_queryset(ContentIndexQuerySet)):
    pass


class ContentIndex(models.Model):
    doc_name_string = models.CharField(max_length=512, null=True, blank=True)
    summary_string = models.CharField(max_length=512, null=True, blank=True)
    file_name_string = models.CharField(max_length=512, null=True, blank=True)
    date_string = VariableDateField()
    content = models.TextField()
    url = models.CharField(max_length=255, blank=True, null=True)
    subjects = models.ManyToManyField(Subject, blank=True, related_name="content")
    document_type = models.ForeignKey(DocumentType, blank=True, null=True, related_name="content", on_delete=models.SET_NULL)
    category = models.ForeignKey(
        AbstractCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name="content"
    )
    locations = models.ManyToManyField(AbstractLocation, blank=True, related_name="content", verbose_name="Regulation Locations")
    resource_type = models.CharField(max_length=25, null=True, blank=True)
    file = models.ForeignKey(UploadedFile, blank=True, null=True, on_delete=models.CASCADE)
    supplemental_content = models.ForeignKey(SupplementalContent, blank=True, null=True, on_delete=models.CASCADE)
    objects = ContentIndexManager()


def create_search(updated_doc, file=None):
    file_content = ''
    if file:
        file_content = file.content
    else:
        # Trigger lambda here to get the text
        file_content = ''
    fi = establish_conntent_type(updated_doc)

    fi.content = file_content
    fi.save()
    fi.locations.set(updated_doc.locations.all())
    fi.subjects.set(updated_doc.subjects.all())
    fi.save()


def establish_conntent_type(updated_doc):
    if isinstance(updated_doc, UploadedFile):
        return ContentIndex(
            file=updated_doc,
            document_type=updated_doc.document_type,
            file_name_string=updated_doc.file_name,
            url=updated_doc.uid,
            doc_name_string=updated_doc.document_name,
            summary_string=updated_doc.summary,
            date_string=updated_doc.date,
            resource_type='internal'
        )
    if isinstance(updated_doc, SupplementalContent):
        return ContentIndex(
            supplemental_content=updated_doc,
            category=updated_doc.category,
            url=updated_doc.url,
            doc_name_string=updated_doc.name,
            summary_string=updated_doc.description,
            date_string=updated_doc.date,
            resource_type='external'
        )
    return None


def update_search(sender, instance, created, **kwargs):
    try:
        if isinstance(instance, UploadedFile):
            file = ContentIndex.objects.get(file=instance)
        if isinstance(instance, SupplementalContent):
            file = ContentIndex.objects.get(supplemental_content=instance)
        create_search(instance, file)
        file.delete()

    except ContentIndex.DoesNotExist:
        create_search(instance)
