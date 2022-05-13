from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.core.exceptions import BadRequest
from django.db.models import Prefetch, Q, Case, When, F
from django.core.exceptions import BadRequest
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter

from django.contrib.postgres.search import SearchHeadline, SearchQuery, SearchVector, SearchRank

from .utils import is_int

from .models import (
    AbstractResource,
    SupplementalContent,
    FederalRegisterDocument,
    AbstractCategory,
    Category,
    SubCategory,
    AbstractLocation,
    Subpart,
    Section,
)

from regcore.views import SettingsAuthentication

from .v3serializers import (
    FederalRegisterDocumentCreateSerializer,
    AbstractCategoryPolymorphicSerializer,
    AbstractLocationPolymorphicSerializer,
    AbstractResourcePolymorphicSerializer,
    SupplementalContentSerializer,
    FederalRegisterDocumentSerializer,
    CategoryTreeSerializer,
    FullSectionSerializer,
    FullSubpartSerializer,
    AbstractResourceSerializer,
    SubCategorySerializer,
    AbstractLocationSerializer,
)
from regcore.serializers import StringListSerializer


def OpenApiQueryParameter(name, description, type, required):
    return OpenApiParameter(name=name, description=description, required=required, type=type, location=OpenApiParameter.QUERY)


# For viewsets where pagination is disabled by default
PAGINATION_PARAMS = [
    OpenApiQueryParameter("page", "A page number within the paginated result set.", int, False),
    OpenApiQueryParameter("page_size", "Number of results to return per page.", int, False),
]


class ViewSetPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 1000
    page_size = 100


# May define "paginate_by_default = False" to disable pagination unless explicitly requested
# Pagination can be enabled/disabled with "?paginate=true/false"
class OptionalPaginationMixin:
    PARAMETERS = [
        OpenApiQueryParameter("paginate", "Enable or disable pagination. If enabled, results will be wrapped in a JSON object. If disabled, a normal JSON array will be returned.", bool, False),
    ]

    paginate_by_default = True

    @property
    def pagination_class(self):
        paginate = self.request.GET.get(
            "paginate",
            "true" if self.paginate_by_default else "false"
        ).lower() == "true"
        return ViewSetPagination if paginate else None


@extend_schema(
    description="Retrieve a flat list of all categories. Pagination is disabled by default.",
    parameters=OptionalPaginationMixin.PARAMETERS + PAGINATION_PARAMS + [
        OpenApiQueryParameter("parent_details", "Show details about each sub-category's parent, rather than just the ID.", bool, False),
    ],
    responses=SubCategorySerializer,
)
class CategoryViewSet(OptionalPaginationMixin, viewsets.ReadOnlyModelViewSet):
    paginate_by_default = False
    queryset = AbstractCategory.objects.all().select_subclasses().select_related("subcategory__parent").order_by("order")
    serializer_class = AbstractCategoryPolymorphicSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["parent_details"] = self.request.GET.get("parent_details", "true")
        return context


@extend_schema(
    description="Retrieve a top-down representation of categories, with each category containing zero or more sub-categories. "
                "Pagination is disabled by default.",
    parameters=OptionalPaginationMixin.PARAMETERS + PAGINATION_PARAMS,
)
class CategoryTreeViewSet(OptionalPaginationMixin, viewsets.ReadOnlyModelViewSet):
    paginate_by_default = False
    queryset = Category.objects.all().select_subclasses().prefetch_related(
        Prefetch("sub_categories", SubCategory.objects.all().order_by("order")),
    ).order_by("order")
    serializer_class = CategoryTreeSerializer


# Must define "location_filter_prefix" (e.g. "" for none, or "locations__")
# May define "location_filter_max_depth" to restrict to searching e.g. titles (=1), or titles and parts (=2)
class LocationFiltererMixin:
    PARAMETERS = [
        OpenApiQueryParameter("locations", "Limit results to only resources linked to these locations. Use \"&locations=X&locations=Y\" for multiple. Examples: 42, 42.433, 42.433.15, 42.433.D.", str, False),
    ]

    location_filter_max_depth = 100

    def get_location_filter(self, locations):
        queries = []
        for loc in locations:
            split = loc.split(".")
            length = len(split)

            if length < 1 or \
               (length >= 1 and not is_int(split[0])) or \
               (length >= 2 and (not is_int(split[0]) or not is_int(split[1]))):
                raise BadRequest(f"\"{loc}\" is not a valid title, part, section, or subpart!")

            q = Q(**{f"{self.location_filter_prefix}title": split[0]})
            if length > 1:
                if self.location_filter_max_depth < 2:
                    raise BadRequest(f"\"{loc}\" is too specific. You may only specify titles.")
                q &= Q(**{f"{self.location_filter_prefix}part": split[1]})
                if length > 2:
                    if self.location_filter_max_depth < 3:
                        raise BadRequest(f"\"{loc}\" is too specific. You may only specify titles and parts.")
                    q &= (
                        Q(**{f"{self.location_filter_prefix}section__section_id": split[2]})
                        if is_int(split[2])
                        else Q(**{f"{self.location_filter_prefix}subpart__subpart_id": split[2]})
                    )

            queries.append(q)
        
        if queries:
            q_obj = queries[0]
            for q in queries[1:]:
                q_obj |= q
            return q_obj
        return None


# Provides a filterable location viewset
class LocationExplorerViewSetMixin(OptionalPaginationMixin, LocationFiltererMixin):
    PARAMETERS = LocationFiltererMixin.PARAMETERS

    location_filter_prefix = ""
    location_filter_max_depth = 2

    def get_queryset(self):
        query = super().get_queryset()

        locations = self.request.GET.getlist("locations")
        q_obj = self.get_location_filter(locations)
        if q_obj:
            query = query.filter(q_obj)

        return query.distinct()


class LocationViewSet(LocationExplorerViewSetMixin, viewsets.ModelViewSet):
    queryset = AbstractLocation.objects.all().select_subclasses()

    authentication_classes = [SettingsAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        description="Retrieve a list of all resource locations, filterable by title and part. Results are paginated by default.",
        parameters=LocationExplorerViewSetMixin.PARAMETERS,
        responses=AbstractLocationSerializer,
    )
    def list(self, request, **kwargs):
        return super(LocationViewSet, self).list(request, **kwargs)
    
    # TODO: extend_schema for this method
    def update(self, request, **kwargs):
        return super(LocationViewSet, self).update(request, **kwargs)  # TODO: implement this!
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return AbstractLocationCreateSerializer
        return AbstractLocationPolymorphicSerializer


@extend_schema(
    description="Retrieve a list of all Section objects, filterable by title and part. Results are paginated by default.",
    parameters=LocationExplorerViewSetMixin.PARAMETERS,
)
class SectionViewSet(OptionalPaginationMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = FullSectionSerializer
    queryset = Section.objects.all().prefetch_related(
        Prefetch("parent", AbstractLocation.objects.all().select_subclasses()),
    )


@extend_schema(
    description="Retrieve a list of all Subpart objects, filterable by title and part. Results are paginated by default.",
    parameters=LocationExplorerViewSetMixin.PARAMETERS,
)
class SubpartViewSet(OptionalPaginationMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = FullSubpartSerializer
    queryset = Subpart.objects.all().prefetch_related(
        Prefetch("children", Section.objects.all()),
    )


# Provides a filterable and searchable viewset for any type of resource
# Must implement get_search_fields() as a map of strings to 2-tuples { "abstract_field_name": ("instance_field_name", "search weight") }
# Must provide "model" as the resource model type to display
# May override compute_dates for complex date lookups
class ResourceExplorerViewSetMixin(OptionalPaginationMixin, LocationFiltererMixin):
    PARAMETERS = [
        OpenApiQueryParameter("category_details", "Specify whether to show details of a category, or just the ID.", bool, False),
        OpenApiQueryParameter("location_details", "Specify whether to show details of a location, or just the ID.", bool, False),
        OpenApiQueryParameter("q", "Search query for resources. Supports literal phrase matching by surrounding the search with quotes.", str, False),
        OpenApiQueryParameter("categories", "Limit results to only resources contained within these categories. Use \"&categories=X&categories=Y\" for multiple.", int, False),
    ] + OptionalPaginationMixin.PARAMETERS + LocationFiltererMixin.PARAMETERS

    location_filter_prefix = "locations__"

    def get_search_fields(self):
        raise NotImplementedError
    
    def compute_dates(self, query):
        return query.annotate(date_annotated=F("date"))
    
    def get_search_map(self):
        fields = {}
        for i in self.get_search_fields().items():
            fields[f"{i[0]}_headline"] = f"{i[1][0]}_headline"
        return fields

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["search_map"] = self.get_search_map()
        context["category_details"] = self.request.GET.get("category_details", "true")
        context["location_details"] = self.request.GET.get("location_details", "true")
        return context

    def get_search_vectors(self):
        fields = list(self.get_search_fields().values())
        v = SearchVector(fields[0][0], weight=fields[0][1], config="english")
        for i in fields[1:]:
            v += SearchVector(i[0], weight=i[1], config="english")
        return v
    
    def get_search_headlines(self, search_query, search_type):
        fields = self.get_search_fields().values()
        annotations = {}
        for field in fields:
            annotations[f"{field[0]}_headline"] = SearchHeadline(
                field[0],
                SearchQuery(search_query, search_type=search_type, config="english"),
                start_sel='<span class="search-headline">',
                stop_sel='</span>',
                config="english",
                highlight_all=True,
            )
        return annotations

    def get_queryset(self):
        query = self.model.objects.all().select_subclasses().prefetch_related(
            Prefetch("locations", AbstractLocation.objects.all().select_subclasses()),
            Prefetch("category", AbstractCategory.objects.all().select_subclasses().select_related("subcategory__parent")),
        )

        locations = self.request.GET.getlist("locations")
        categories = self.request.GET.getlist("categories")
        search_query = self.request.GET.get("q")

        q_obj = self.get_location_filter(locations)
        if q_obj:
            query = query.filter(q_obj)
        
        if categories:
            query = query.filter(category__id__in=categories)

        if search_query:
            (search_type, cover_density) = (
                ("phrase", True)
                if search_query.startswith('"') and search_query.endswith('"')
                else ("plain", False)
            )

            query = query.annotate(rank=SearchRank(
                self.get_search_vectors(),
                SearchQuery(search_query, search_type=search_type, config="english"),
                cover_density=cover_density,
            )).filter(rank__gte=0.2).annotate(**self.get_search_headlines(search_query, search_type))

        return self.compute_dates(query.distinct()).order_by("-rank" if search_query else "-date_annotated")


@extend_schema(
    description="Retrieve a list of all resources. Includes all types e.g. supplemental content, Federal Register Documents, etc. "
                "Searching is supported as well as inclusive filtering by title, part, subpart, and section. "
                "Results are paginated by default.",
    parameters=ResourceExplorerViewSetMixin.PARAMETERS,
    responses=AbstractResourceSerializer,
)
class AbstractResourceViewSet(ResourceExplorerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = AbstractResourcePolymorphicSerializer
    model = AbstractResource

    def compute_dates(self, query):
        return query.annotate(date_annotated=Case(
            When(supplementalcontent__isnull=False, then=F("supplementalcontent__date")),
            When(federalregisterdocument__isnull=False, then=F("federalregisterdocument__date")),
            default=None,
        ))

    def get_search_fields(self):
        return {
            "supplementalcontent__name": ("supplementalcontent__name", "A"),
            "supplementalcontent__description": ("supplementalcontent__description", "A"),
            "federalregisterdocument__name": ("federalregisterdocument__name", "A"),
            "federalregisterdocument__description": ("federalregisterdocument__description", "A"),
            "federalregisterdocument__docket_number": ("federalregisterdocument__docket_number", "A"),
            "federalregisterdocument__document_number": ("federalregisterdocument__document_number", "A"),
        }


@extend_schema(
    description="Retrieve a list of all supplemental content. "
                "Searching is supported as well as inclusive filtering by title, part, subpart, and section. "
                "Results are paginated by default.",
    parameters=ResourceExplorerViewSetMixin.PARAMETERS,
)
class SupplementalContentViewSet(ResourceExplorerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = SupplementalContentSerializer
    model = SupplementalContent

    def get_search_fields(self):
        return {
            "supplementalcontent__name": ("name", "A"),
            "supplementalcontent__description": ("description", "A"),
        }


class FederalRegisterDocsViewSet(ResourceExplorerViewSetMixin, viewsets.ModelViewSet):
    model = FederalRegisterDocument

    authentication_classes = [SettingsAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        description="Retrieve a list of all Federal Register Documents. "
                    "Searching is supported as well as inclusive filtering by title, part, subpart, and section. "
                    "Results are paginated by default.",
        parameters=ResourceExplorerViewSetMixin.PARAMETERS,
    )
    def list(self, request, **kwargs):
        return super(FederalRegisterDocsViewSet, self).list(request, **kwargs)

    @extend_schema(description="Upload a Federal Register Document to the eRegs Resources system. "
                               "If the document already exists, it will be updated.")
    def update(self, request, **kwargs):
        data = request.data
        frdoc, created = FederalRegisterDocument.objects.get_or_create(document_number=data["document_number"])
        data["id"] = frdoc.pk
        sc = self.get_serializer(frdoc, data=data)
        try:
            if sc.is_valid(raise_exception=True):
                sc.save()
                response = sc.validated_data
                return JsonResponse(response)
        except Exception as e:
            if created:
                frdoc.delete()
            raise e

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return FederalRegisterDocumentCreateSerializer
        return FederalRegisterDocumentSerializer

    def get_search_fields(self):
        return {
            "federalregisterdocument__name": ("name", "A"),
            "federalregisterdocument__description": ("description", "A"),
            "federalregisterdocument__docket_number": ("docket_number", "A"),
            "federalregisterdocument__document_number": ("document_number", "A"),
        }


@extend_schema(
    description="Retrieve a list of document numbers from all Federal Register Documents. "
                "Pagination is disabled by default.",
    parameters=OptionalPaginationMixin.PARAMETERS + PAGINATION_PARAMS,
    responses={(200, "application/json"): {"type": "string"}},
)
class FederalRegisterDocsNumberViewSet(OptionalPaginationMixin, viewsets.ReadOnlyModelViewSet):
    paginate_by_default = False
    queryset = FederalRegisterDocument.objects.all().values_list("document_number", flat=True).distinct()
    serializer_class = StringListSerializer
