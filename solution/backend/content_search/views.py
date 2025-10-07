from django.db.models import Count, F, Prefetch, Q
from django.http import QueryDict
from django.urls import reverse
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.response import Response

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

from .models import (
    ContentIndex,
    IndexedRegulationText,
    ResourceMetadata,
)
from .serializers import (
    ContentCountSerializer,
    ContentSearchSerializer,
    ResourceChunkUpdateSerializer,
)


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


class ResourceChunkUpdateViewSet(viewsets.ViewSet):
    def update(self, request, *args, **kwargs):
        # Validate the request body
        serializer = ResourceChunkUpdateSerializer(data=request.data)
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
        response_text += f" {deleted} extra chunks deleted." if deleted else ""
        return Response(response_text)
