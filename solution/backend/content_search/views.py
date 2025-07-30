import boto3
import json

from django.db.models import Count, F, Prefetch, Q
from django.http import QueryDict
from django.urls import reverse
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.response import Response

from django.db.models.functions import Lower, Substr
from django.views.generic import TemplateView
from django.http import JsonResponse
from pgvector import django as pgvector_django

from cmcs_regulations.utils.api_exceptions import BadRequest
from cmcs_regulations.utils.pagination import ViewSetPagination
from regulations.utils import LinkConfigMixin, LinkConversionsMixin
from resources.models import (
    AbstractCategory,
    AbstractCitation,
    AbstractResource,
    Subject,
)
from resources.utils import get_citation_filter, string_to_bool

from .models import ContentIndex, IndexedRegulationText, TextEmbedding
from .serializers import ContentCountSerializer, ContentSearchSerializer


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
        # Get query
        query = request.POST.get("query")
        if not query:
            return JsonResponse({"error": "Query parameter 'query' is required."}, status=400)
        if len(query) > 20000:
            return JsonResponse({"error": "Query parameter 'query' must be less than 20,000 characters."}, status=400)
        query = " ".join(query.split()).lower()  # Remove extra spaces and convert to lowercase

        # Validate the distance algorithm
        distance_algorithm = request.POST.get("distance_algorithm")
        distance_function = getattr(pgvector_django, distance_algorithm, None)
        if not distance_function:
            return JsonResponse({"error": f"Invalid distance algorithm: {distance_algorithm}"}, status=400)

        include_content = "include_content" in request.POST
        filter_duplicates = "filter_duplicates" in request.POST
        max_distance = float(request.POST.get("max_distance", 5))
        max_results = int(request.POST.get("max_results", 10))

        # Use Bedrock to perform a vector search
        client = boto3.client(
            'bedrock-runtime',
            region_name="us-east-1",
            # aws_access_key_id="",
            # aws_secret_access_key="",
            # aws_session_token="",
        )
        try:
            payload = {
                "inputText": query,
                "dimensions": 512,
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

        # Perform the vector search using the embedding
        embeddings = TextEmbedding.objects.prefetch_related(Prefetch("index", ContentIndex.objects.all())).annotate(
            **{"distance": distance_function('embedding', embedding)},
            **{"content": Substr("index__content", F("start_offset"), 20000)} if include_content else {},
        ).filter(distance__lt=max_distance).order_by('distance')[:max_results]

        # Get values to return
        values = ("index__name", "index__id", "index__resource__id", "index__resource__document_id",
                  "index__resource__title", "index__reg_text__id", "index__reg_text__title", "index__reg_text__part",
                  "index__reg_text__node_type", "index__reg_text__node_id", "distance", "start_offset")
        if include_content:
            values += ("content",)
        results = embeddings.values(*values)

        # Remove dupes
        if filter_duplicates:
            seen = set()
            unique_results = []
            for item in results:
                if item["index__id"] not in seen:
                    seen.add(item["index__id"])
                    unique_results.append(item)
            results = unique_results

        # Return the results as a JSON response
        return JsonResponse([{
            "name": i["index__name"],
            "id": i["index__id"],
            "resource": {
                "id": i["index__resource__id"],
                "document_id": i["index__resource__document_id"],
                "title": i["index__resource__title"],
            } if i["index__resource__id"] else None,
            "reg_text": {
                "id": i["index__reg_text__id"],
                "title": i["index__reg_text__title"],
                "part": i["index__reg_text__part"],
                "node_type": i["index__reg_text__node_type"],
                "node_id": i["index__reg_text__node_id"],
            } if i["index__reg_text__id"] else None,
            "distance": i["distance"],
            "start_offset": i["start_offset"],
            "content": i.get("content", None),
        } for i in results], safe=False)


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
