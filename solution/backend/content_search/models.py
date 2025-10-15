
from django.conf import settings
from django.contrib.postgres.search import (
    SearchHeadline,
    SearchQuery,
    SearchRank,
    SearchVectorField,
)
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F
from django.db.models.expressions import RawSQL
from django.db.models.functions import Substr
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_jsonform.models.fields import JSONField
from pgvector.django import VectorField
from solo.models import SingletonModel

from common.constants import QUOTE_TYPES
from regcore.models import Part
from resources.models import (
    AbstractResource,
    FederalRegisterLink,
    InternalFile,
    InternalLink,
    PublicLink,
)


class ContentSearchConfiguration(SingletonModel):
    auto_extract = models.BooleanField(
        default=False,
        help_text="Check this box if eRegs should automatically request text extraction on any resource when it is originally "
                  "saved/created or when its source is changed: URL (for public and internal links), document number "
                  "(for FR links), or attached file (for internal files).",
        verbose_name="Auto Extract",
    )

    extraction_delay_time = models.IntegerField(
        default=180,  # Default to 3 minutes
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="The number of seconds to delay between multiple text extraction requests. This is useful to prevent "
                  "overloading external services with too many requests in a short period of time.",
        verbose_name="Extraction Delay Time",
    )

    robots_txt_allow_list = JSONField(
        default=list,
        blank=True,
        help_text="A list of URLs and/or domains that the text extractor should be allowed to access, even if eRegs is not in "
                  "their robots.txt file. For example, 'example.com' will allow the entire domain and all subdomains to be "
                  "accessed, while 'https://example.com/page.html' will allow only that specific page.",
        verbose_name="Robots.txt Allow List",
        schema={
            "type": "list",
            "minItems": 0,
            "items": {
                "type": "string",
                "title": "URL or Domain",
                "placeholder": "example.com",
            },
        },
        pre_save_hook=lambda value: [url for url in [url.strip().lower() for url in value] if url],
    )

    user_agent_override_list = JSONField(
        default=list,
        blank=True,
        help_text="A list of domains and user agents that the text extractor should use instead of the default user agent. "
                  "This is useful for sites that block eRegs' default user agent. Note that a domain will match all subdomains.",
        verbose_name="User Agent Override List",
        schema={
            "type": "list",
            "minItems": 0,
            "items": {
                "type": "object",
                "title": "Domain and User Agent",
                "properties": {
                    "domain": {
                        "type": "string",
                        "title": "Domain",
                        "placeholder": "example.com",
                    },
                    "user_agent": {
                        "type": "string",
                        "title": "User Agent (optional)",
                        "placeholder": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
                    },
                },
                "required": ["domain"],
            },
        },
        pre_save_hook=lambda value: [
            {"domain": item["domain"].strip(), "user_agent": item.get("user_agent", "").strip()}
            for item in value if item.get("domain")
        ],
    )

    default_user_agent_override = models.CharField(
        max_length=255,
        blank=True,
        help_text="A default user agent to use for all requests to domains in the user agent override list that do not "
                  "specify a user agent. This is useful for sites that block eRegs' default user agent.",
        verbose_name="Default User Agent Override",
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    )

    def __str__(self):
        return "Content Search Configuration"

    class Meta:
        verbose_name = "Content Search Configuration"


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

    def defer_text(self):
        return self.defer(
            "name",
            "summary",
            "content",
            "rank_a_string",
            "rank_b_string",
            "rank_c_string",
            "rank_d_string",
        )

    def search(self, search_query, sort_method="-rank"):
        cover_density = self._is_quoted(search_query)
        rank_filter = float(settings.QUOTED_SEARCH_FILTER if cover_density else settings.BASIC_SEARCH_FILTER)

        if sort_method == "-date":
            order_by = (F("date").desc(nulls_last=True), F("resource__title").asc(nulls_last=True))

        elif sort_method == "date":
            order_by = (F("date").asc(nulls_last=True), F("resource__title").asc(nulls_last=True))

        else:
            order_by = ("-rank", "-date", "-id")

        return self.annotate(
            rank=SearchRank(
                RawSQL("vector_column", [], output_field=SearchVectorField()),
                self._get_search_query_object(search_query), cover_density=cover_density
            )
        )\
        .filter(rank__gt=rank_filter)\
        .order_by(*order_by)\


    def generate_headlines(self, search_query):
        query_object = self._get_search_query_object(search_query)
        return self.annotate(content_short=Substr("content", 1, self._text_max)).annotate(
            summary_headline=SearchHeadline(
                "summary",
                query_object,
                start_sel="<span class='search-highlight'>",
                stop_sel='</span>',
                config='english',
                highlight_all=True,
                fragment_delimiter='...',
            ),
            name_headline=SearchHeadline(
                "name",
                query_object,
                start_sel="<span class='search-highlight'>",
                stop_sel="</span>",
                config='english',
                highlight_all=True,
                fragment_delimiter='...',
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


class ResourceMetadata(models.Model):
    resource = models.OneToOneField(AbstractResource, on_delete=models.CASCADE, related_name="index_metadata")

    # Fields populated using a post-save hook on the eRegs side
    name = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    date = models.CharField(max_length=10, null=True)
    rank_a_string = models.TextField(blank=True)
    rank_b_string = models.TextField(blank=True)
    rank_c_string = models.TextField(blank=True)
    rank_d_string = models.TextField(blank=True)

    detected_file_type = models.CharField(
        max_length=32,
        blank=True,
        help_text="The file type that the text extractor detected for this resource.",
        editable=False,
    )
    extraction_error = models.TextField(
        blank=True,
        help_text="If the text extractor failed to extract text from this resource, the error message will be stored here.",
        editable=False,
    )

    def __str__(self):
        return f"Indexed Resource: {self.resource}"


class IndexedRegulationText(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    title = models.IntegerField(default=0)
    date = models.DateField(blank=True, null=True)
    part_title = models.TextField(blank=True)
    part_number = models.IntegerField(default=0)
    subpart_title = models.TextField(blank=True)
    subpart_id = models.CharField(max_length=8, blank=True)
    node_type = models.CharField(max_length=32, blank=True)
    node_id = models.CharField(max_length=32, blank=True)
    node_title = models.TextField(blank=True)


# This model is an all encompassing searchable index allowing different models to share an index.
# Instead of recalculating the vector column each time a change in weights are done the values will be stored
# in the rank_{}_string fields. Also supports vector embeddings via pgvector.
class ContentIndex(models.Model):
    # Fields used for generating search headlines
    name = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    date = models.CharField(max_length=10, null=True)

    # Rank fields for searching
    rank_a_string = models.TextField(blank=True)
    rank_b_string = models.TextField(blank=True)
    rank_c_string = models.TextField(blank=True)
    rank_d_string = models.TextField(blank=True)

    # ForeignKey fields linked to possible indexed types (arbitrary # of indices per document)
    resource = models.ForeignKey(AbstractResource, blank=True, null=True, on_delete=models.CASCADE, related_name="indices")
    reg_text = models.ForeignKey(IndexedRegulationText, blank=True, null=True, on_delete=models.CASCADE, related_name="indices")

    # Text extraction metadata for resources only
    resource_metadata = models.OneToOneField(
        ResourceMetadata,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="index_metadata",
    )

    # Fields for managing chunks
    content = models.TextField(blank=True)
    embedding = VectorField(dimensions=512, default=None, null=True, blank=True)
    chunk_index = models.IntegerField(default=0)

    objects = ContentIndexManager()

    class Meta:
        verbose_name = "Content Index"
        verbose_name_plural = "Content Indices"
        indexes = [
            models.Index(fields=["-date"]),
            models.Index(fields=["resource"]),
            models.Index(fields=["reg_text"]),
            models.Index(fields=["chunk_index"]),
            models.Index(fields=["embedding"]),
        ]
        unique_together = (
            ("resource", "chunk_index"),
            ("reg_text", "chunk_index"),
        )
        ordering = ("resource", "reg_text", "chunk_index")


def update_indexed_resource(resource, fields):
    metadata, _ = ResourceMetadata.objects.update_or_create(resource=resource, defaults=fields)
    ContentIndex.objects.filter(resource_metadata=metadata).update(**fields)


@receiver(post_save, sender=PublicLink)
@receiver(post_save, sender=FederalRegisterLink)
def update_indexed_public_resource(sender, instance, created, **kwargs):
    update_indexed_resource(instance, {
        "name": instance.document_id,
        "summary": instance.title,
        "date": instance.date or None,
        "rank_a_string": "{} {}".format(
            instance.document_id,
            instance.title,
        ),
        "rank_b_string": "",
        "rank_c_string": instance.date,
        "rank_d_string": " ".join([str(i) for i in instance.subjects.all()]),
    })


@receiver(post_save, sender=InternalFile)
def update_indexed_internal_file(sender, instance, created, **kwargs):
    update_indexed_resource(instance, {
        "name": instance.title,
        "summary": instance.summary,
        "date": instance.date or None,
        "rank_a_string": instance.title,
        "rank_b_string": instance.summary,
        "rank_c_string": "{} {}".format(
            instance.date,
            instance.file_name,
        ),
        "rank_d_string": " ".join([str(i) for i in instance.subjects.all()]),
    })


@receiver(post_save, sender=InternalLink)
def update_indexed_internal_link(sender, instance, created, **kwargs):
    update_indexed_resource(instance, {
        "name": instance.title,
        "summary": instance.summary,
        "date": instance.date or None,
        "rank_a_string": instance.title,
        "rank_b_string": instance.summary,
        "rank_c_string": instance.date,
        "rank_d_string": " ".join([str(i) for i in instance.subjects.all()]),
    })
