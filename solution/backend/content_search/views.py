import json

from django.contrib.postgres.search import (
    SearchHeadline,
    SearchQuery,
)
from django.db import connection, transaction
from django.db.models import Count, F, Prefetch, Q
from django.db.models.functions import Substr
from django.http import QueryDict
from django.urls import reverse
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import exceptions, viewsets
from rest_framework.parsers import FormParser
from rest_framework.response import Response

from cmcs_regulations.utils.api_exceptions import BadRequest
from cmcs_regulations.utils.pagination import ViewSetPagination
from common.aws import establish_client
from common.constants import QUOTE_TYPES
from common.exceptions import ServiceUnavailable
from regulations.utils import LinkConfigMixin, LinkConversionsMixin
from resources.models import (
    AbstractCategory,
    AbstractCitation,
    AbstractResource,
    Subject,
)
from resources.utils import get_citation_filter, string_to_bool

from .models import (
    ContentIndex,
    ContentSearchConfiguration,
    IndexedRegulationText,
    ResourceMetadata,
)
from .serializers import (
    ChunkUpdateSerializer,
    ContentCountSerializer,
    ContentSearchQuerySerializer,
    ContentSearchSerializer,
)
from .utils import preprocess_text


def _get_parameter(name, request, default=None):
    return request.GET.get(name) or request.POST.get(name) or default


def _get_parameter_list(name, request):
    return request.GET.getlist(name) or request.POST.getlist(name)


class ContentSearchMixin:
    PARAMETERS = [
        OpenApiParameter(
            name="q",
            required=False,
            type=str,
            description=(
                "Search for this text within public and internal resources, and regulation text. "
                "Fields searched depends on the underlying data type. "
                "Use either 'q' or 'query' as the parameter name."
            ),
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="citations",
            required=False,
            type=int,
            description=(
                "Limit results to only resources linked to these citations. Use \"&citations=X&citations=Y\" "
                "for multiple. Examples: 42, 42.433, 42.433.15, 42.433.D."
            ),
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="subjects",
            required=False,
            type=int,
            description=(
                "Limit results to only resources found within these subjects. Subjects are referenced by ID, not name. "
                "Use \"&subjects=1&subjects=2\" for multiple."
            ),
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="categories",
            required=False,
            type=int,
            description=(
                "Limit results to only resources found within these categories. Categories are referenced by ID, not "
                "name. Use \"&categories=1&categories=2\" for multiple."
            ),
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="show_public",
            required=False,
            type=bool,
            description="Whether to include public resources in the search results.",
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="show_internal",
            required=False,
            type=bool,
            description="Whether to include internal resources in the search results.",
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="show_regulations",
            required=False,
            type=bool,
            description="Whether to include regulation text in the search results.",
            location=OpenApiParameter.QUERY,
        ),
    ]

    def is_quoted(self, query):
        return query.startswith(QUOTE_TYPES) and query.endswith(QUOTE_TYPES)

    def generate_embedding(self, query):
        response = establish_client("bedrock-runtime").invoke_model(
            modelId="amazon.titan-embed-text-v2:0",
            body=json.dumps({
                "inputText": query,
                "dimensions": 512,
                "normalize": True,
            }),
            contentType="application/json",
            accept="application/json",
        )
        return json.loads(response.get("body").read())["embedding"]

    def search(self, query, config):
        query = query or ""  # Ensure query is a string

        # Get optional parameters (from query string or form body)
        citations = _get_parameter_list("citations", self.request)
        subjects = _get_parameter_list("subjects", self.request)
        categories = _get_parameter_list("categories", self.request)
        show_public = string_to_bool(_get_parameter("show_public", self.request), True)
        show_internal = string_to_bool(_get_parameter("show_internal", self.request), True)
        show_regulations = string_to_bool(_get_parameter("show_regulations", self.request), True)

        # Retrieve content search configuration
        min_rank = config.keyword_search_min_rank
        max_distance = config.semantic_search_max_distance
        k_value = config.rrf_k_value
        enable_semantic = config.enable_semantic_search
        enable_keyword = config.enable_keyword_search
        keyword_search_max_words = config.keyword_search_max_words
        semantic_search_min_words = config.semantic_search_min_words
        use_keyword_search_for_quoted = config.use_keyword_search_for_quoted

        # Determine the search and headline generation strategy

        # Default (unquoted) keyword search config
        keyword_rank_func = "ts_rank"
        keyword_search_type = "plain"

        query_words = len(query.split())  # Rough word count

        # Disable keyword search for long queries if semantic is enabled (keyword search is too slow for very long queries)
        if enable_semantic and query_words > keyword_search_max_words:
            enable_keyword = False

        # Disable semantic search for short queries if keyword is enabled (results aren't meaningful for very short queries)
        if enable_keyword and query_words < semantic_search_min_words:
            enable_semantic = False

        if query:
            query = preprocess_text(query)
        else:
            enable_keyword = enable_semantic = False

        # Adjust strategy for quoted queries
        if self.is_quoted(query) and enable_keyword:
            keyword_rank_func = "ts_rank_cd"
            keyword_search_type = "phrase"
            query = query.strip("".join(QUOTE_TYPES))
            if use_keyword_search_for_quoted:
                enable_semantic = False

        # Generate embedding if needed
        embedding = None
        if enable_semantic:
            try:
                embedding = self.generate_embedding(query.lower())
            except Exception:
                raise ServiceUnavailable("Failed to generate embedding for semantic search. Please try again later.")

        # Perform initial filtering
        q_filter = ~Q(resource__approved=False)

        # Filter inclusively by citations if this array exists
        q_filter &= get_citation_filter(citations, "resource__cfr_citations__")

        # Filter by subject pks if subjects array is present
        if subjects:
            q_filter &= Q(resource__subjects__pk__in=subjects)

        # Filter by categories (both parent and subcategories) if the categories array is present
        if categories:
            q_filter &= (
                Q(resource__category__pk__in=categories) |
                Q(resource__category__abstractpubliccategory__publicsubcategory__parent__pk__in=categories) |
                Q(resource__category__abstractinternalcategory__internalsubcategory__parent__pk__in=categories)
            )

        # Filter by public, internal, and regulation text
        if not show_public:
            q_filter &= ~Q(resource__abstractpublicresource__isnull=False)
        if not show_internal or not self.request.user.is_authenticated:
            q_filter &= ~Q(resource__abstractinternalresource__isnull=False)
        if not show_regulations:
            q_filter &= ~Q(reg_text__isnull=False)

        # Convert the queryset to raw SQL while preserving safe parameterization
        query_object = ContentIndex.objects.filter(q_filter).only("id").query
        sql_compiler = query_object.get_compiler(connection=connection)
        sql_filter, sql_params = query_object.as_sql(sql_compiler, connection)
        sql_filter = sql_filter.replace("%s", "{}").format(*[f"%(pos{i})s" for i in range(len(sql_params))])
        sql_params = {f"pos{i}": param for i, param in enumerate(sql_params)}

        # Define initial CTE that filters by the above criteria
        sql = "WITH indices AS ( " + sql_filter + " )"

        if enable_semantic or enable_keyword:
            sql += ", "

        # If neither semantic nor keyword search is enabled, return all filtered results with a score of 0.0
        if not (enable_semantic or enable_keyword):
            sql += """
                SELECT
                    id,
                    0.0 AS score
                FROM content_search_contentindex
                WHERE id IN (SELECT id FROM indices)
                ORDER BY date DESC NULLS LAST, id DESC
            """

        # If semantic is enabled, add semantic search CTE
        if enable_semantic:
            sql += """
                semantic_search AS (
                    SELECT
                        id,
                        resource_id,
                        reg_text_id,
                        rank
                    FROM (
                        SELECT
                            id,
                            resource_id,
                            reg_text_id,
                            embedding,
                            raw_rank,
                            RANK () OVER (ORDER BY raw_rank ASC) AS rank
                        FROM (
                            SELECT
                                id,
                                resource_id,
                                reg_text_id,
                                embedding,
                                embedding <=> (%(embedding)s::vector) AS raw_rank
                            FROM content_search_contentindex
                            WHERE id IN (SELECT id FROM indices)
                        ) AS raw_rank_table
                    ) AS rank_table
                    WHERE embedding IS NOT NULL
                    AND (resource_id IS NOT NULL OR reg_text_id IS NOT NULL)
                    AND raw_rank < %(max_distance)s
                )
            """

        # If hybrid search is enabled, add a comma to separate the semantic and full-text CTEs
        if enable_semantic and enable_keyword:
            sql += ", "

        # If full-text search is enabled, add full-text search CTE
        # Note that we disable S608 warning here because the query is properly parameterized therefore is safe from SQL injection
        # The linter is complaining because we insert the function names dynamically, but those are set by us and not user input
        if enable_keyword:
            sql += f"""
                keyword_search AS (
                    SELECT
                        id,
                        resource_id,
                        reg_text_id,
                        rank
                    FROM (
                        SELECT
                            id,
                            resource_id,
                            reg_text_id,
                            raw_rank,
                            RANK () OVER (ORDER BY raw_rank DESC) AS rank
                        FROM (
                            SELECT
                                id,
                                resource_id,
                                reg_text_id,
                                {keyword_rank_func}(
                                    (vector_column),
                                    {keyword_search_type}to_tsquery('english', %(query)s)
                                ) AS raw_rank
                            FROM content_search_contentindex
                            WHERE id IN (SELECT id FROM indices)
                        ) AS raw_rank_table
                    ) AS rank_table
                    WHERE (resource_id IS NOT NULL OR reg_text_id IS NOT NULL)
                    AND raw_rank > %(min_rank)s
                )
            """  # noqa S608

        # Retrieve data for semantic search only
        if enable_semantic and not enable_keyword:
            sql += """
                SELECT
                    id,
                    rank AS score
                FROM (
                    SELECT DISTINCT ON (resource_id, reg_text_id)
                        id,
                        rank
                    FROM semantic_search
                    ORDER BY resource_id ASC, reg_text_id ASC
                ) AS distinct_table
                ORDER BY score ASC
            """

        # Retrieve data for full-text search only
        if enable_keyword and not enable_semantic:
            sql += """
                SELECT
                    id,
                    rank AS score
                FROM (
                    SELECT DISTINCT ON (resource_id, reg_text_id)
                        id,
                        rank
                    FROM keyword_search
                    ORDER BY resource_id ASC, reg_text_id ASC
                ) AS distinct_table
                ORDER BY score ASC
            """

        # Combine and retrieve both semantic and full-text results
        if enable_semantic and enable_keyword:
            sql += """
                SELECT
                    id,
                    score
                FROM (
                    SELECT DISTINCT ON (resource_id, reg_text_id)
                        COALESCE(semantic_search.id, keyword_search.id) AS id,
                        COALESCE(semantic_search.resource_id, keyword_search.resource_id) AS resource_id,
                        COALESCE(semantic_search.reg_text_id, keyword_search.reg_text_id) AS reg_text_id,
                        COALESCE(1.0 / (%(k)s + semantic_search.rank), 0.0) +
                            COALESCE(1.0 / (%(k)s + keyword_search.rank), 0.0) AS score
                    FROM semantic_search
                    FULL OUTER JOIN keyword_search ON semantic_search.id = keyword_search.id
                    ORDER BY resource_id ASC, reg_text_id ASC
                ) AS combined_table
                ORDER BY score DESC
            """

        # Execute the raw SQL query
        return ContentIndex.objects.raw(sql, {**sql_params, **{
            "embedding": embedding,
            "query": query,
            "k": k_value,
            "max_distance": max_distance,
            "min_rank": min_rank,
        }})


@extend_schema(
    tags=["content_search"],
    description=(
        "Retrieve search results for a given set of filters. "
        "Searches public and internal resources, and regulation text. "
        "Note that internal resources are only shown if the user is authenticated. "
        "Subjects and categories are listed only by PK. To retrieve more metadata about these types, use the subjects "
        "and categories endpoints available within the Resources app."
    ),
    responses={200: ContentSearchSerializer},
    parameters=ContentSearchMixin.PARAMETERS,
    methods=["GET", "POST"],
    request=ContentSearchQuerySerializer,
)
class ContentSearchViewSet(ContentSearchMixin, LinkConfigMixin, LinkConversionsMixin, viewsets.ReadOnlyModelViewSet):
    model = ContentIndex
    serializer_class = ContentSearchSerializer
    pagination_class = ViewSetPagination
    parser_classes = (FormParser,)

    def list(self, request, *args, **kwargs):
        # Retrieve content search configuration and query
        config = ContentSearchConfiguration.get_solo()
        headline_text_max = config.headline_text_max_length
        headline_min_words = config.headline_min_words
        headline_max_words = config.headline_max_words
        headline_max_fragments = config.headline_max_fragments
        query = _get_parameter("query", request) or _get_parameter("q", request) or ""

        # Get the initial filtered and ranked search results
        search_results = self.search(query, config)

        # Paginate, then generate headlines on the current page only (for performance)
        current_page = [i.pk for i in self.paginate_queryset(search_results)]
        search_type = "phrase" if self.is_quoted(query) else "plain"
        query_object = SearchQuery(query, search_type=search_type, config="english")
        queryset = ContentIndex.objects.defer_text().filter(pk__in=current_page).annotate(
            content_short=Substr("content", 1, headline_text_max),
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
                min_words=headline_min_words,
                max_words=headline_max_words,
                fragment_delimiter='...',
                max_fragments=headline_max_fragments,
            ),
        )

        # Prefetch all related data
        queryset = queryset.prefetch_related(
            Prefetch("reg_text", IndexedRegulationText.objects.all()),
            Prefetch("resource", AbstractResource.objects.select_subclasses().prefetch_related(
                Prefetch("cfr_citations", AbstractCitation.objects.select_subclasses()),
                Prefetch("category", AbstractCategory.objects.select_subclasses().prefetch_related(
                    Prefetch("parent", AbstractCategory.objects.select_subclasses()),
                )),
                Prefetch("subjects", Subject.objects.all()),
            )),
        )

        # Sort the current page by rank
        queryset = sorted(queryset, key=lambda x: current_page.index(x.pk))

        # Serialize and return the results
        serializer = self.get_serializer_class()(queryset, many=True, context=self.get_serializer_context())
        return self.get_paginated_response(serializer.data)


@extend_schema(
    tags=["content_search"],
    description="Retrieve the number of results for a given set of filters. "
                "This endpoint allows you to get the number of results per type (public, internal, reg-text) "
                "without retrieving the actual content. Useful for pagination and displaying the number of results. "
                "Note that internal resources are only counted if the user is authenticated. "
                "This endpoint also displays the number of resources found within each subject and category that have results. "
                "Subjects and categories are listed only by PK. To retrieve more metadata about these types, use the subjects "
                "and categories endpoints available within the Resources app.",
    responses={200: ContentCountSerializer},
    request=ContentSearchQuerySerializer,
    parameters=ContentSearchMixin.PARAMETERS,
    methods=["GET", "POST"],
)
class ContentCountViewSet(ContentSearchMixin, viewsets.ViewSet):
    parser_classes = (FormParser,)

    # Used for automatically generating a URL to the count endpoint
    def generate_url(request):
        new_get = QueryDict(mutable=True)
        [new_get.update({i: j}) for i, j in request.GET.items() if i in ["q", "query", "citations", "subjects", "categories"]]
        return request.build_absolute_uri(reverse("content_count")) + f"?{new_get.urlencode()}"

    def list(self, request, *args, **kwargs):
        # Retrieve content search configuration and query
        config = ContentSearchConfiguration.get_solo()
        query = _get_parameter("query", request) or _get_parameter("q", request)

        # Get the initial filtered and ranked search results
        search_results = self.search(query, config)

        # Retrieve the primary keys of the filtered results to speed up the following queries
        pks = [i.id for i in search_results]

        # Aggregate the counts of internal, public, and reg text
        aggregates = ContentIndex.objects.filter(pk__in=pks).aggregate(
            internal_resource_count=Count("resource", filter=Q(resource__abstractinternalresource__isnull=False)),
            public_resource_count=Count("resource", filter=Q(resource__abstractpublicresource__isnull=False)),
            regulation_text_count=Count("reg_text"),
        )

        # List of subjects that are in the results and the number of resources in the result set that are associated with them
        aggregates["subjects"] = AbstractResource.objects \
            .filter(indices__pk__in=pks) \
            .exclude(subjects__isnull=True) \
            .values("subjects") \
            .annotate(subject=F("subjects"), count=Count("subjects")) \
            .values("subject", "count") \
            .order_by("-count", "subject")

        # List of categories that are in the results and the number of resources in the result set that are associated with them
        # Note that resources are already filtered by user visibility, so by extension, we don't need to filter categories
        aggregates["categories"] = AbstractResource.objects \
            .filter(indices__pk__in=pks) \
            .exclude(category__isnull=True) \
            .values("category") \
            .annotate(parent=F("category__parent"), count=Count("category")) \
            .order_by("-count", "category")

        # Serialize and return the results
        return Response(ContentCountSerializer(aggregates).data)


@extend_schema(
    tags=["content_search"],
    description="Update or create a content index chunk for a given resource.",
    request=ChunkUpdateSerializer,
    responses={200: str},
)
class ResourceChunkUpdateViewSet(viewsets.ViewSet):
    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        # Validate the request body
        serializer = ChunkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Get data from the request body
        resource_id = data["id"]
        chunk_index = data["chunk_index"]
        total_chunks = data["total_chunks"]
        file_type = data["file_type"]
        error = data["error"]
        text = data["text"]
        embedding = data["embedding"]

        # Get the resource (and ensure it exists, otherwise fail)
        try:
            resource = AbstractResource.objects.get(pk=resource_id)
        except AbstractResource.DoesNotExist:
            raise BadRequest(f"Resource with id {resource_id} does not exist.")

        # Update resource metadata (and ensure it exists, otherwise fail)
        try:
            metadata = ResourceMetadata.objects.get(resource=resource)
            if metadata.detected_file_type != file_type or metadata.extraction_error != error:
                metadata.detected_file_type = file_type
                metadata.extraction_error = error
                metadata.save()
        except ResourceMetadata.DoesNotExist:
            raise BadRequest(f"Resource with id {resource_id} does not have associated metadata.")

        # Delete any extra chunks that may exist beyond the new total_chunks value
        deleted, _ = ContentIndex.objects.filter(Q(resource=resource) & Q(chunk_index__gte=total_chunks)).delete()

        # Update or create the chunk
        index, created = ContentIndex.objects.update_or_create(
            resource=resource,
            chunk_index=chunk_index,
            defaults={
                "name": metadata.name,
                "summary": metadata.summary,
                "date": metadata.date,
                "rank_a_string": metadata.rank_a_string,
                "rank_b_string": metadata.rank_b_string,
                "rank_c_string": metadata.rank_c_string,
                "rank_d_string": metadata.rank_d_string,
                "resource_metadata": metadata,
                "content": text,
                "embedding": embedding,
            }
        )

        response_text = f"Chunk {index.pk} for {resource._meta.verbose_name} {resource.pk} successfully" \
                        f"{'created' if created else 'updated'}."
        response_text += f" {deleted} extra chunk(s) deleted." if deleted else ""
        return Response(response_text)


@extend_schema(
    tags=["content_search"],
    description="Update or create a content index chunk for a given slice of regulation text, e.g., a section or appendix.",
    request=ChunkUpdateSerializer,
    responses={200: str},
)
class RegTextChunkUpdateViewSet(viewsets.ViewSet):
    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        # Validate the request body
        serializer = ChunkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Get data from the request body
        reg_text_id = data["id"]
        chunk_index = data["chunk_index"]
        total_chunks = data["total_chunks"]
        text = data["text"]
        embedding = data["embedding"]

        # Retrieve reg text metadata (and ensure it exists, otherwise fail)
        try:
            reg_text = IndexedRegulationText.objects.get(pk=reg_text_id)
        except IndexedRegulationText.DoesNotExist:
            raise BadRequest(f"Reg text metadata object with id {reg_text_id} does not exist.")

        # Delete any extra chunks that may exist beyond the new total_chunks value
        deleted, _ = ContentIndex.objects.filter(Q(reg_text=reg_text) & Q(chunk_index__gte=total_chunks)).delete()

        # Update or create the chunk
        index, created = ContentIndex.objects.update_or_create(
            reg_text=reg_text,
            chunk_index=chunk_index,
            defaults={
                "name": reg_text.name,
                "summary": reg_text.summary,
                "date": reg_text.date,
                "rank_a_string": f"{reg_text.node_id} {reg_text.node_title}",
                "rank_b_string": f"{reg_text.part_title}",
                "rank_c_string": f"{text}",
                "rank_d_string": "",
                "content": text,
                "embedding": embedding,
            }
        )

        response_text = f"Chunk {index.pk} for {reg_text.title} CFR {reg_text.part_number} {reg_text.node_type} " \
                        f"{reg_text.node_id} successfully {'created' if created else 'updated'}."
        response_text += f" {deleted} extra chunk(s) deleted." if deleted else ""
        return Response(response_text)
