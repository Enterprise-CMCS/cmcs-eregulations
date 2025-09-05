import json

import boto3
from django.db import transaction, connection
from django.db.models import Count, F, Prefetch, Q
from django.db.models.functions import Substr
from django.http import JsonResponse, QueryDict
from django.urls import reverse
from django.views.generic import TemplateView
from drf_spectacular.utils import OpenApiParameter, extend_schema
from pgvector import django as pgvector_django
from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cmcs_regulations.utils.api_exceptions import BadRequest, ExceptionSerializer
from cmcs_regulations.utils.pagination import ViewSetPagination
from common.auth import SettingsAuthentication
from regulations.utils import LinkConfigMixin, LinkConversionsMixin
from resources.models import (
    AbstractCategory,
    AbstractCitation,
    AbstractResource,
    Subject,
)
from resources.utils import get_citation_filter, string_to_bool

from .models import ContentIndex, IndexedRegulationText, TextEmbedding
from .serializers import ContentCountSerializer, ContentSearchSerializer, EmbeddingSerializer

import unicodedata
from bs4 import BeautifulSoup
import html
import re


def preprocess_text(text: str) -> str:
    # Remove unicode control characters
    text = "".join(ch if not unicodedata.category(ch).lower().startswith("c") else " " for ch in text).strip()
    # Re-encode as unicode-escaped
    text = text.encode("unicode_escape").decode("unicode_escape")
    # Remove HTML elements
    text = html.unescape(text)
    text = BeautifulSoup(text, "html.parser").get_text()
    # Collapse whitespace and convert to lowercase
    text = " ".join(text.split()).lower()
    # Replace non-alphanumeric but repeated characters with max 3 instances if repeated 3 or more times
    # (e.g. -------------------- turns into ---)
    text = re.sub(r"([^\s\w]{3,})", repl=lambda match: match.group()[0]*3, string=text)
    return text


class ContentSearchPagination(ViewSetPagination):
    def get_additional_attributes(self):
        return {**super().get_additional_attributes(), **{
            "count_url": ContentCountViewSet.generate_url(self.request),
        }}

    def get_additional_attribute_schemas(self):
        return {**super().get_additional_attribute_schemas(), **{
            "count_url": {
                "type": "string",
                "format": "uri",
                "nullable": True,
                "example": "http://api.example.org/content_count/?q=example",
            },
        }}


@extend_schema(
    tags=["content_search"],
    description="Search and retrieve content with highlighted matching terms. "
                "This endpoint allows you to search through both resources and regulation texts, "
                "returning relevant content with highlighted matches in the name, summary, and content fields.",
    responses={200: ContentSearchSerializer(many=True)},
    parameters=[
        OpenApiParameter(
            name="subjects",
            required=False,
            type=int,
            description="Limit results to only resources found within these subjects. Subjects are referenced by ID, not name. "
                        "Use \"&subjects=1&subjects=2\" for multiple.",
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="categories",
            required=False,
            type=int,
            description="Limit results to only resources found within these categories. Categories are referenced by ID, not "
                        "name. Use \"&categories=1&categories=2\" for multiple.",
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="q",
            required=True,
            type=str,
            description="Search for this text within public and internal resources, and regulation text. "
                        "Fields searched depends on the underlying data type.",
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="show_public",
            required=False,
            type=str,
            description="Show ('true') or hide ('false') public resources, including Federal Register and other public links. "
                        "Default is true.",
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="show_internal",
            required=False,
            type=str,
            description="Show ('true') or hide ('false') internal resources, including files and internal links. "
                        "Default is true. Note that internal resources are only shown if the user is authenticated. "
                        "If the user is not authenticated, this flag will have no effect.",
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="show_regulations",
            required=False,
            type=str,
            description="Show ('true') or hide ('false') regulation text, including sections and appendices. "
                        "Default is true.",
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="citations",
            required=False,
            type=int,
            description="Limit results to only resources linked to these citations. Use \"&citations=X&citations=Y\" "
                        "for multiple. Examples: 42, 42.433, 42.433.15, 42.433.D",
            location=OpenApiParameter.QUERY,
        ),
    ] + ViewSetPagination.QUERY_PARAMETERS,
)
class ContentSearchViewSet(LinkConfigMixin, LinkConversionsMixin, viewsets.ReadOnlyModelViewSet):
    model = ContentIndex
    serializer_class = ContentSearchSerializer
    pagination_class = ContentSearchPagination

    def list(self, request, *args, **kwargs):
        citations = request.GET.getlist("citations")
        subjects = request.GET.getlist("subjects")
        categories = request.GET.getlist("categories")
        sort = request.GET.get("sort")
        show_public = string_to_bool(request.GET.get("show_public"), True)
        show_internal = string_to_bool(request.GET.get("show_internal"), True)
        show_regulations = string_to_bool(request.GET.get("show_regulations"), True)

        # Retrieve the required search query param
        search_query = request.GET.get("q")
        if not search_query:
            raise BadRequest("A search query is required; provide 'q' parameter in the query string.")

        # Defer all unnecessary text fields to reduce database load and memory usage
        query = ContentIndex.objects.defer_text()

        # Filter out unapproved resources
        query = query.exclude(resource__approved=False)

        # Filter inclusively by citations if this array exists
        citation_filter = get_citation_filter(citations, "resource__cfr_citations__")
        if citation_filter:
            query = query.filter(citation_filter)

        # Filter by subject pks if subjects array is present
        if subjects:
            query = query.filter(resource__subjects__pk__in=subjects)

        # Filter by categories (both parent and subcategories) if the categories array is present
        if categories:
            query = query.filter(
                Q(resource__category__pk__in=categories) |
                Q(resource__category__abstractpubliccategory__publicsubcategory__parent__pk__in=categories) |
                Q(resource__category__abstractinternalcategory__internalsubcategory__parent__pk__in=categories)
            )

        # Filter by public, internal, and regulation text
        if not show_public:
            query = query.exclude(resource__abstractpublicresource__isnull=False)
        if not show_internal or not self.request.user.is_authenticated:
            query = query.exclude(resource__abstractinternalresource__isnull=False)
        if not show_regulations:
            query = query.exclude(reg_text__isnull=False)

        # Perform search and headline generation
        query = query.search(search_query, sort)

        current_page = [i.pk for i in self.paginate_queryset(query)]
        query = ContentIndex.objects.defer_text().filter(pk__in=current_page).generate_headlines(search_query)

        # Prefetch all related data
        query = query.prefetch_related(
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
        query = sorted(query, key=lambda x: current_page.index(x.pk))

        # Serialize and return the results
        serializer = self.get_serializer_class()(query, many=True, context=self.get_serializer_context())
        return self.get_paginated_response(serializer.data)


class PgVectorSearchView(TemplateView):
    template_name = "pgvector_search.html"

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        # Get query and preprocess it
        query = request.POST.get("query")
        if not query:
            return JsonResponse({"error": "Query parameter 'query' is required."}, status=400)
        if len(query) > 10000:
            return JsonResponse({"error": "Query parameter 'query' must be less than 10,000 characters."}, status=400)
        query = preprocess_text(query)

        # Get additional params
        include_content = "include_content" in request.POST
        filter_duplicates = "filter_duplicates" in request.POST
        min_rank = float(request.POST.get("min_rank", 0.1))
        max_distance = float(request.POST.get("max_distance", 1.3))
        k_value = int(request.POST.get("k_value", 60))
        max_results = int(request.POST.get("max_results", 10))
        search_type = request.POST.get("search_type", "hybrid")

        # Rank ordering params
        full_text_over_rank_order = request.POST.get("full_text_over_rank_order", "DESC")
        full_text_final_rank_order = request.POST.get("full_text_final_rank_order", "ASC")
        semantic_over_rank_order = request.POST.get("semantic_over_rank_order", "ASC")
        semantic_final_rank_order = request.POST.get("semantic_final_rank_order", "ASC")

        # Define a client factory with optional AWS keys
        make_boto3_client = lambda client: boto3.client(client, **{k: v for k, v in {
            "region_name": "us-east-1",
            "aws_access_key_id": request.POST.get("aws_access_key_id"),
            "aws_secret_access_key": request.POST.get("aws_secret_access_key"),
            "aws_session_token": request.POST.get("aws_session_token"),
        }.items() if v})

        # Use Bedrock to generate embedding for query
        client = make_boto3_client('bedrock-runtime')
        try:
            payload = {
                "inputText": query,
                "dimensions": 512,
                "normalize": True,
            }
            response = client.invoke_model(
                modelId="amazon.titan-embed-text-v2:0",
                body=json.dumps(payload),
                contentType="application/json",
                accept="application/json",
            )
            embedding = json.loads(response.get("body").read())["embedding"]
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        # Define initial SQL
        sql = "WITH "

        # If semantic is enabled, add semantic search CTE
        if search_type in ["semantic", "hybrid"]:
            sql += f"""
                semantic_search AS (
                    SELECT
                        "content_search_textembedding"."id" AS "chunk_id",
                        "content_search_textembedding"."index_id" AS "id",
                        "content_search_contentindex"."name" AS "name",
                        "content_search_contentindex"."summary" AS "summary",
                        "content_search_contentindex"."resource_id" AS "resource_id",
                        "content_search_contentindex"."reg_text_id" AS "reg_text_id",
                        "content_search_textembedding"."start_offset",
                        embedding <=> (%(embedding)s::vector) AS raw_rank,
                        RANK () OVER (ORDER BY embedding <=> (%(embedding)s::vector) {semantic_over_rank_order}) AS rank
                    FROM content_search_textembedding
                    JOIN content_search_contentindex
                        ON content_search_textembedding.index_id = content_search_contentindex.id
                    WHERE embedding <=> (%(embedding)s::vector) < %(max_distance)s
                    ORDER BY embedding <=> (%(embedding)s::vector) {semantic_final_rank_order}
                )
            """

        # If hybrid search is enabled, add a comma to separate the semantic and full-text CTEs
        if search_type == "hybrid":
            sql += ", "

        # If full-text search is enabled, add full-text search CTE
        if search_type in ["full_text", "hybrid"]:
            sql += f"""
                keyword_search AS (
                    SELECT
                        "content_search_contentindex"."id",
                        "content_search_contentindex"."name",
                        "content_search_contentindex"."summary",
                        "content_search_contentindex"."resource_id",
                        "content_search_contentindex"."reg_text_id",
                        0 AS "start_offset",
                        ts_rank((vector_column), plainto_tsquery('english', %(query)s)) AS raw_rank,
                        RANK () OVER (ORDER BY ts_rank((vector_column), plainto_tsquery('english', %(query)s)) {full_text_over_rank_order}) AS rank
                    FROM "content_search_contentindex"
                    WHERE ts_rank((vector_column), plainto_tsquery('english', %(query)s)) > %(min_rank)s
                    ORDER BY rank {full_text_final_rank_order}, "content_search_contentindex"."date" DESC, "content_search_contentindex"."id" DESC
                )
            """

        # Retrieve data for semantic search only
        if search_type == "semantic":
            sql += """
                SELECT
                    semantic_search.id,
                    semantic_search.name,
                    semantic_search.summary,
                    semantic_search.rank AS score,
                    semantic_search.raw_rank AS semantic_raw_rank,
                    null AS keyword_raw_rank,
                    semantic_search.start_offset,
                    semantic_search.resource_id,
                    semantic_search.reg_text_id
                FROM semantic_search
            """

        # Retrieve data for full-text search only
        if search_type == "full_text":
            sql += """
                SELECT
                    keyword_search.id,
                    keyword_search.name,
                    keyword_search.summary,
                    keyword_search.rank AS score,
                    null AS semantic_raw_rank,
                    keyword_search.raw_rank AS keyword_raw_rank,
                    keyword_search.start_offset,
                    keyword_search.resource_id,
                    keyword_search.reg_text_id
                FROM keyword_search
            """

        # Combine and retrieve both semantic and full-text results
        if search_type == "hybrid":
            sql += """
                SELECT
                    COALESCE(semantic_search.id, keyword_search.id) AS id,
                    COALESCE(semantic_search.name, keyword_search.name) AS name,
                    COALESCE(semantic_search.summary, keyword_search.summary) AS summary,
                    COALESCE(1.0 / (%(k)s + semantic_search.rank), 0.0) +
                    COALESCE(1.0 / (%(k)s + keyword_search.rank), 0.0) AS score,
                    COALESCE(semantic_search.raw_rank, 0.0) AS semantic_raw_rank,
                    COALESCE(keyword_search.raw_rank, 0.0) AS keyword_raw_rank,
                    COALESCE(semantic_search.start_offset, keyword_search.start_offset) AS start_offset,
                    COALESCE(semantic_search.resource_id, keyword_search.resource_id) AS resource_id,
                    COALESCE(semantic_search.reg_text_id, keyword_search.reg_text_id) AS reg_text_id
                FROM semantic_search
                FULL OUTER JOIN keyword_search ON semantic_search.id = keyword_search.id
                ORDER BY score DESC
            """

        # Execute the query and retrieve the results
        with connection.cursor() as cursor:
            cursor.execute(sql, {
                "embedding": embedding,
                "query": query,
                "k": k_value,
                "max_results": max_results,
                "max_distance": max_distance,
                "min_rank": min_rank,
            })
            results = cursor.fetchall()

        results = [{
            "index_id": i[0],
            "name": i[1],
            "summary": i[2],
            "score": i[3],
            "semantic_raw_rank": i[4],
            "keyword_raw_rank": i[5],
            "start_offset": i[6],
            "resource_id": i[7],
            "reg_text_id": i[8],
            "content": None,
        } for i in results]

        # Ensure uniqueness if filter_duplicates is true
        if filter_duplicates:
            seen = set()
            unique_results = []
            for item in results:
                if item["index_id"] not in seen:
                    seen.add(item["index_id"])
                    unique_results.append(item)
            results = unique_results

        # Limit the number of results
        if max_results:
            results = results[:max_results]

        # Get contents field
        if include_content:
            contents = ContentIndex.objects.filter(id__in=[i["index_id"] for i in results]).values("id", "content")
            contents = {i["id"]: i["content"] for i in contents}
            for i in results:
                text = contents.get(i["index_id"])
                if not text:
                    i["content"] = None
                    continue
                start = i.get("start_offset") or 0
                # In reality, the chunk goes to the end of the nearest word, however an explicit 11,000 is sufficient for testing
                end = min(start + 10000 + 1000, len(text))
                i["content"] = text[start:end]

        # Return the results as a JSON response
        return JsonResponse(results, safe=False)


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
    parameters=[
        OpenApiParameter(
            name="q",
            required=False,
            type=str,
            description="Search for this text within public and internal resources, and regulation text. "
                        "Fields searched depends on the underlying data type.",
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="citations",
            required=False,
            type=int,
            description="Limit results to only resources linked to these citations. Use \"&citations=X&citations=Y\" "
                        "for multiple. Examples: 42, 42.433, 42.433.15, 42.433.D",
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="subjects",
            required=False,
            type=int,
            description="Limit results to only resources found within these subjects. Subjects are referenced by ID, not name. "
                        "Use \"&subjects=1&subjects=2\" for multiple.",
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="categories",
            required=False,
            type=int,
            description="Limit results to only resources found within these categories. Categories are referenced by ID, not "
                        "name. Use \"&categories=1&categories=2\" for multiple.",
            location=OpenApiParameter.QUERY,
        ),
    ],
)
class ContentCountViewSet(viewsets.ViewSet):
    # Used for automatically generating a URL to the count endpoint
    def generate_url(request):
        new_get = QueryDict(mutable=True)
        [new_get.update({i: j}) for i, j in request.GET.items() if i in ["q", "citations", "subjects", "categories"]]
        return request.build_absolute_uri(reverse("content_count")) + f"?{new_get.urlencode()}"

    def list(self, request, *args, **kwargs):
        # Retrieve optional parameters
        citations = request.GET.getlist("citations")
        subjects = request.GET.getlist("subjects")
        categories = request.GET.getlist("categories")
        search_query = request.GET.get("q")

        # Defer all unnecessary text fields to reduce database load and memory usage
        query = ContentIndex.objects.defer_text()

        # Filter out unapproved resources
        query = query.exclude(resource__approved=False)

        # Filter inclusively by citations if this array exists
        citation_filter = get_citation_filter(citations, "resource__cfr_citations__")
        if citation_filter:
            query = query.filter(citation_filter)

        # Filter by subject pks if subjects array is present
        if subjects:
            query = query.filter(resource__subjects__pk__in=subjects)

        # Filter by categories (both parent and subcategories) if the categories array is present
        if categories:
            query = query.filter(
                Q(resource__category__pk__in=categories) |
                Q(resource__category__abstractpubliccategory__publicsubcategory__parent__pk__in=categories) |
                Q(resource__category__abstractinternalcategory__internalsubcategory__parent__pk__in=categories)
            )

        # Filter out internal resources if the user is not authenticated
        if not self.request.user.is_authenticated:
            query = query.exclude(resource__abstractinternalresource__isnull=False)

        # Perform search if 'q' parameter exists
        if search_query:
            query = query.search(search_query)

        # Retrieve the primary keys of the filtered results to speed up the following queries
        pks = list(query.values_list("pk", flat=True))

        # Aggregate the counts of internal, public, and reg text
        aggregates = ContentIndex.objects.filter(pk__in=pks).aggregate(
            internal_resource_count=Count("resource", filter=Q(resource__abstractinternalresource__isnull=False)),
            public_resource_count=Count("resource", filter=Q(resource__abstractpublicresource__isnull=False)),
            regulation_text_count=Count("reg_text"),
        )

        # List of subjects that are in the results and the number of resources in the result set that are associated with them
        aggregates["subjects"] = AbstractResource.objects \
            .filter(index__pk__in=pks) \
            .exclude(subjects__isnull=True) \
            .values("subjects") \
            .annotate(subject=F("subjects"), count=Count("subjects")) \
            .values("subject", "count") \
            .order_by("-count", "subject")

        # List of categories that are in the results and the number of resources in the result set that are associated with them
        # Note that resources are already filtered by user visibility, so by extension, we don't need to filter categories
        aggregates["categories"] = AbstractResource.objects \
            .filter(index__pk__in=pks) \
            .exclude(category__isnull=True) \
            .values("category") \
            .annotate(parent=F("category__parent"), count=Count("category")) \
            .order_by("-count", "category")

        # Serialize and return the results
        return Response(ContentCountSerializer(aggregates).data)


@extend_schema(
    tags=["content_search"],
    description="Update an existing text embedding with new data. "
                "This endpoint allows you to update the embedding of a specific text chunk by its ID.",
    request=EmbeddingSerializer,
    responses={200: str, 404: ExceptionSerializer},
)
class EmbeddingViewSet(APIView):
    """
    ViewSet for updating text embeddings.
    This view allows for updating existing text embeddings with new data.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [SettingsAuthentication]

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        serializer = EmbeddingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        pk = kwargs.get("id", data.get("id"))
        if not pk:
            raise NotFound("The ID of the object to update must be passed in.")

        try:
            chunk = TextEmbedding.objects.get(pk=pk)
        except TextEmbedding.DoesNotExist:
            raise NotFound(f"An embedding chunk matching ID {pk} does not exist.")

        # Update the embedding chunk with the new data
        chunk.embedding = data.get("embedding", chunk.embedding)
        chunk.save()

        return Response(data=f"Embedding chunk {pk} updated successfully.", status=200)
