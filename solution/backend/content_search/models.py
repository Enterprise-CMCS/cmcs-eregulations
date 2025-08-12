import logging
import re
from functools import partial
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.postgres.search import (
    SearchHeadline,
    SearchQuery,
    SearchRank,
    SearchVectorField,
)
from django.db import models
from django.db.models import F
from django.db.models.expressions import RawSQL
from django.db.models.functions import Substr
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from pgvector.django import VectorField

from common import aws_utils
from common.constants import QUOTE_TYPES
from content_search.utils import remove_control_characters
from regcore.models import Part
from regulations.middleware import get_site_uri
from resources.models import (
    AbstractResource,
    FederalRegisterLink,
    InternalFile,
    InternalLink,
    PublicLink,
    ResourceContent,
)

logger = logging.getLogger(__name__)


class Synonym(models.Model):
    is_active = models.BooleanField(default=True)
    base_word = models.CharField(max_length=128)
    synonyms = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return self.base_word if self.is_active else f'{self.base_word} (inactive)'


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


class IndexedRegulationText(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    title = models.IntegerField(default=0)
    date = models.DateField(blank=True, null=True)
    part_title = models.TextField(blank=True)
    part_number = models.IntegerField(default=0)
    node_type = models.CharField(max_length=32, blank=True)
    node_id = models.CharField(max_length=32, blank=True)
    node_title = models.TextField(blank=True)


# This model is an all encompassing searchable index allowing different models to share an index.
# Instead of recalculating the vector column each time a change in weights are done the values will be stored
# in the rank_{}_string fields.
class ContentIndex(models.Model):
    # Fields used for generating search headlines
    name = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    content = models.TextField(blank=True)
    date = models.CharField(max_length=10, null=True)

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


class TextEmbedding(models.Model):
    index = models.ForeignKey(ContentIndex, on_delete=models.CASCADE, related_name="embeddings")
    embedding = VectorField(dimensions=512, default=None, null=True, blank=True)
    chunk_index = models.IntegerField()
    start_offset = models.IntegerField()

    class Meta:
        unique_together = (("index", "chunk_index"),)
        verbose_name = "Text Embedding"
        verbose_name_plural = "Text Embeddings"
        indexes = [
            models.Index(fields=["index"]),
            models.Index(fields=["embedding"]),
        ]


def chunk_text(text, max_length=20000, overlap=1000):
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_length, len(text))
        chunk = text[start:end]
        chunks.append((start, chunk))
        if end == len(text):
            break
        start += max_length - overlap
    return chunks


@receiver(post_save, sender=ContentIndex)
def update_text_embeddings(sender, instance, created, **kwargs):
    """
    Create or update text embeddings for the ContentIndex instance.
    This is triggered whenever a ContentIndex instance is saved.
    If the site's URI is not available due to this save being invoked without a request,
    the embeddings will not be generated.
    """

    site_uri = get_site_uri()
    if not site_uri:
        logger.warning("No site URI found, cannot generate embeddings.")
        return

    # Prepare the text for embedding
    if instance.resource and instance.content:
        act_citations = " ".join([
            f"{citation['act']} {citation['section']}"
            for citation in instance.resource.act_citations
            if citation
        ])
        usc_citations = " ".join([
            f"{citation['title']} {citation['section']}"
            for citation in instance.resource.usc_citations
            if citation
        ])
        document_id = instance.resource.document_id or ""
        title = instance.resource.title or ""
        text = " ".join([
            act_citations,
            usc_citations,
            document_id,
            title,
            *instance.content.split(),
        ]).lower()
    elif instance.reg_text:
        metadata = instance.reg_text
        text = " ".join([
            str(metadata.title),
            "CFR",
            str(metadata.part_number),
            metadata.node_type,
            metadata.node_id,
            *instance.content.split(),
        ]).lower()
    else:
        logger.warning("No valid metadata found for ContentIndex instance %i", instance.id)
        return

    # Delete existing embeddings for the instance
    TextEmbedding.objects.filter(index=instance).delete()

    # Split the text into chunks and create embeddings for each chunk
    chunks = chunk_text(text)
    embeddings = TextEmbedding.objects.bulk_create([
        TextEmbedding(
            index=instance,
            chunk_index=chunk_index,
            start_offset=start,
        ) for chunk_index, (start, chunk) in enumerate(chunks)
    ])

    # Send embeddings to the embedding generator queue
    requests = [{
        "id": embedding.id,
        "upload_url": (
            f"{settings.LOCAL_EREGS_URL}{reverse('embedding_upload', args=[embedding.id])}"
            if settings.USE_LOCAL_EMBEDDING_GENERATOR else
            urljoin(site_uri, reverse('embedding_upload', args=[embedding.id]))
        ),
        "text": embedding.text,
        "auth": {
            "type": "basic",
            "username": settings.HTTP_AUTH_USER,
            "password": settings.HTTP_AUTH_PASSWORD,
        } if settings.USE_LOCAL_EMBEDDING_GENERATOR else {
            "type": "basic-secretsmanager-env",
            "secret_name": "SECRET_NAME",
            "username_key": "username",
            "password_key": "password",
        },
    } for embedding in embeddings]

    if settings.USE_LOCAL_EMBEDDING_GENERATOR:
        invoke_function = partial(
            aws_utils.invoke_via_http,
            url=settings.LOCAL_EMBEDDING_GENERATOR_URL,
        )
    elif settings.EMBEDDING_GENERATOR_QUEUE_URL:
        invoke_function = partial(
            aws_utils.invoke_via_sqs,
            client=aws_utils.get_aws_client("sqs"),
            url=settings.EMBEDDING_GENERATOR_QUEUE_URL,
        )
    elif settings.EMBEDDING_GENERATOR_ARN:
        invoke_function = partial(
            aws_utils.invoke_via_lambda,
            client=aws_utils.get_aws_client("lambda"),
            arn=settings.EMBEDDING_GENERATOR_ARN,
        )
    else:
        logger.warning("No valid embedding generator configuration found.")
        return

    for batch in [requests[i:i + 10] for i in range(0, len(requests), 10)]:
        # Send each batch to the embedding generator queue
        _, failures = invoke_function(batch)
        if failures:
            # Log the failures
            for failure in failures:
                logger.error("Failed to send embedding for chunk %i: %s", failure["id"], failure["reason"])


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
    index.date = instance.date or None
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
    index.date = instance.date or None
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
    index.date = instance.date or None
    index.rank_a_string = instance.title
    index.rank_b_string = instance.summary
    index.rank_c_string = instance.date
    index.rank_d_string = " ".join([str(i) for i in instance.subjects.all()])
    index.save()


def index_part_node(part, piece, indices, contents, parent=None):
    try:
        node_type = piece.get("node_type", "").lower()
        part_number, node_id = {
            "section": (0, 1),
            "appendix": (6, 3),
        }[node_type]

        label = piece["label"]
        part_number = int(label[part_number])
        node_id = remove_control_characters(label[node_id])

        content = piece.get("title", piece.get("text", ""))
        children = piece.pop("children", []) or []
        for child in children:
            content += child.get("text", "") + re.sub('<[^<]+?>', "", child.get("content", ""))

        contents.append(remove_control_characters(content))
        indices.append(IndexedRegulationText(
            part=part,
            title=part.title,
            date=part.date,
            part_title=remove_control_characters(part.document["title"]),
            part_number=part_number,
            node_type=node_type,
            node_id=node_id,
            node_title=remove_control_characters(piece["title"]),
        ))

    except Exception:
        children = piece.pop("children", []) or []
        for child in children:
            index_part_node(part, child, indices, contents, parent=piece)

    return indices, contents


@receiver(post_save, sender=Part)
def update_indexed_part(sender, instance, created, **kwargs):
    # Delete all previously indexed parts with the same name and title
    parts = Part.objects.filter(name=instance.name, title=instance.title)
    IndexedRegulationText.objects.filter(part__in=parts).delete()

    # Only index the latest version of the part
    part = parts.latest("date")
    indices, contents = index_part_node(part, part.document, [], [])
    indices = IndexedRegulationText.objects.bulk_create(indices)
    ContentIndex.objects.bulk_create([ContentIndex(
        name=i.node_title,
        content=c,
        reg_text=i,
        rank_a_string=f"{i.node_id} {i.node_title}",
        rank_b_string=f"{i.part_title}",
        rank_c_string=f"{c}",
        rank_d_string="",
    ) for i, c in zip(indices, contents)])
