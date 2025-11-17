
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_jsonform.models.fields import JSONField
from pgvector.django import VectorField
from solo.models import SingletonModel

from regcore.models import Part
from resources.models import (
    AbstractResource,
    FederalRegisterLink,
    InternalFile,
    InternalLink,
    PublicLink,
)


class ContentSearchConfiguration(SingletonModel):
    enable_keyword_search = models.BooleanField(
        default=True,
        help_text="Enable traditional keyword-based search for precise matching of search terms.",
        verbose_name="Enable Keyword Search",
    )

    enable_semantic_search = models.BooleanField(
        default=True,
        help_text="Enable semantic search using vector embeddings for more relevant search results.",
        verbose_name="Enable Semantic Search",
    )

    keyword_search_min_rank = models.FloatField(
        default=0.1,
        validators=[MinValueValidator(0.0)],
        help_text="Minimum rank threshold for keyword search results to be included.",
        verbose_name="Keyword Search Minimum Rank",
    )

    keyword_search_min_rank_quoted = models.FloatField(
        default=0.01,
        validators=[MinValueValidator(0.0)],
        help_text="Minimum rank threshold for keyword search results to be included when the query is quoted.",
        verbose_name="Keyword Search Minimum Rank for Quoted Queries",
    )

    semantic_search_max_distance = models.FloatField(
        default=1.3,
        validators=[MinValueValidator(0.0)],
        help_text="Maximum distance threshold for semantic search results to be included.",
        verbose_name="Semantic Search Maximum Distance",
    )

    rrf_k_value = models.IntegerField(
        default=60,
        validators=[MinValueValidator(1)],
        help_text="The 'k' value used in the Reciprocal Rank Fusion (RRF) "
                  "algorithm to combine keyword and semantic search results.",
        verbose_name="RRF K Value",
    )

    semantic_search_min_words = models.IntegerField(
        default=2,
        validators=[MinValueValidator(1)],
        help_text="Minimum number of words required in the search query to allow semantic search if keyword search is enabled.",
        verbose_name="Semantic Search Minimum Words",
    )

    keyword_search_max_words = models.IntegerField(
        default=15,
        validators=[MinValueValidator(1)],
        help_text="Maximum number of words allowed in the search query to enable keyword search if semantic search is enabled.",
        verbose_name="Keyword Search Maximum Words",
    )

    use_keyword_search_for_quoted = models.BooleanField(
        default=True,
        help_text="Use keyword search for quoted search queries to ensure exact phrase matching.",
        verbose_name="Use Keyword Search for Quoted Queries",
    )

    headline_text_max_length = models.IntegerField(
        default=10000,
        validators=[MinValueValidator(1)],
        help_text="Maximum length of text to consider when generating search result headlines.",
        verbose_name="Headline Text Maximum Length",
    )

    headline_min_words = models.IntegerField(
        default=50,
        validators=[MinValueValidator(1)],
        help_text="Minimum number of words in each headline fragment.",
        verbose_name="Headline Minimum Words",
    )

    headline_max_words = models.IntegerField(
        default=51,
        validators=[MinValueValidator(1)],
        help_text="Maximum number of words in each headline fragment.",
        verbose_name="Headline Maximum Words",
    )

    headline_max_fragments = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Maximum number of headline fragments to generate. Set to 0 for no limit.",
        verbose_name="Headline Maximum Fragments",
    )

    generate_embeddings = models.BooleanField(
        default=True,
        help_text="Generate vector embeddings during text extraction to enable semantic search.",
        verbose_name="Generate Embeddings",
    )

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
