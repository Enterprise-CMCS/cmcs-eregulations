from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.core.exceptions import BadRequest
from django.db.models import Prefetch, Q, Case, When, F
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db import transaction

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
    StringListSerializer,
)


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
        OpenApiQueryParameter("paginate", "Enable or disable pagination. If enabled, results will be wrapped in a JSON object. "
                              "If disabled, a normal JSON array will be returned.", bool, False),
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
        OpenApiQueryParameter("parent_details", "Show details about each sub-category's parent, rather "
                              "than just the ID.", bool, False),
    ],
    responses=SubCategorySerializer,
)
class CategoryViewSet(OptionalPaginationMixin, viewsets.ReadOnlyModelViewSet):
    paginate_by_default = False
    serializer_class = AbstractCategoryPolymorphicSerializer
    queryset = AbstractCategory.objects.all().select_subclasses().select_related("subcategory__parent")\
                               .order_by("order").contains_fr_docs()

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
        Prefetch("sub_categories", SubCategory.objects.all().order_by("order").contains_fr_docs()),
    ).order_by("order").contains_fr_docs()
    serializer_class = CategoryTreeSerializer


# Must define "location_filter_prefix" (e.g. "" for none, or "locations__")
# May define "location_filter_max_depth" to restrict to searching e.g. titles (=1), or titles and parts (=2)
class LocationFiltererMixin:
    PARAMETERS = [
        OpenApiQueryParameter("locations",
                              "Limit results to only resources linked to these locations. Use \"&locations=X&locations=Y\" "
                              "for multiple. Examples: 42, 42.433, 42.433.15, 42.433.D.", str, False),
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
    PARAMETERS = LocationFiltererMixin.PARAMETERS + OptionalPaginationMixin.PARAMETERS

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
        # if self.request.method == "POST":  # TODO: implement AbstractLocationCreateSerializer
        #     return AbstractLocationCreateSerializer
        return AbstractLocationPolymorphicSerializer


@extend_schema(
    description="Retrieve a list of all Section objects, filterable by title and part. Results are paginated by default.",
    parameters=LocationExplorerViewSetMixin.PARAMETERS,
)
class SectionViewSet(LocationExplorerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = FullSectionSerializer
    queryset = Section.objects.all().prefetch_related(
        Prefetch("parent", AbstractLocation.objects.all().select_subclasses()),
    )


@extend_schema(
    description="Retrieve a list of all Subpart objects, filterable by title and part. Results are paginated by default.",
    parameters=LocationExplorerViewSetMixin.PARAMETERS,
)
class SubpartViewSet(LocationExplorerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = FullSubpartSerializer
    queryset = Subpart.objects.all().prefetch_related(
        Prefetch("children", Section.objects.all()),
    )


# Provides a filterable and searchable viewset for any type of resource
# Must implement get_search_fields() as a list of fields or a map of model names to lists of fields
# Must provide "model" as the resource model type to display
# May override get_annotated_date() for complex date lookups
# May override get_annotated_group() to limit particular model types to one result per group
#     (By default, -1*pk is used so that no resource gets removed)
class ResourceExplorerViewSetMixin(OptionalPaginationMixin, LocationFiltererMixin):
    PARAMETERS = [
        OpenApiQueryParameter("category_details", "Specify whether to show details of a category, or just the ID.", bool, False),
        OpenApiQueryParameter("location_details", "Specify whether to show details of a location, or just the ID.", bool, False),
        OpenApiQueryParameter("q", "Search query for resources. Supports literal phrase matching by surrounding the "
                              "search with quotes.", str, False),
        OpenApiQueryParameter("categories", "Limit results to only resources found within these categories. Use "
                              "\"&categories=X&categories=Y\" for multiple.", int, False),
        OpenApiQueryParameter("sort", "Sort results by this field. Valid values are \"newest\", \"oldest\", and \"relevance\". "
                              "Newest is the default, and relevance requires a search query.", str, False),
        OpenApiQueryParameter("fr_grouping", "Determines if FR Documents should be grouped or not"
                              "Default is true", bool, False),
    ] + OptionalPaginationMixin.PARAMETERS + LocationFiltererMixin.PARAMETERS

    location_filter_prefix = "locations__"

    def get_search_fields(self):
        raise NotImplementedError

    def get_annotated_date(self):
        return F("date")

    def get_annotated_group(self):
        return -1*F("pk")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["category_details"] = self.request.GET.get("category_details", "true")
        context["location_details"] = self.request.GET.get("location_details", "true")
        context["fr_grouping"] = self.request.GET.get("fr_grouping", "true")
        return context

    def get_search_vectors(self):
        v = None
        search_fields = self.get_search_fields()
        if isinstance(search_fields, type([])):
            for field in search_fields:
                vector = SearchVector(field, weight="A", config="english")
                v = v + vector if v else vector
        else:
            for model in search_fields:
                for field in search_fields[model]:
                    vector = SearchVector(f"{model}__{field}", weight="A", config="english")
                    v = v + vector if v else vector
        return v

    def make_headline(self, field, search_query, search_type):
        return SearchHeadline(
            field,
            SearchQuery(search_query, search_type=search_type, config="english"),
            start_sel='<span class="search-headline">',
            stop_sel='</span>',
            config="english",
            highlight_all=True,
        )

    def get_search_headlines(self, search_query, search_type):
        annotations = {}
        search_fields = self.get_search_fields()
        if isinstance(search_fields, type([])):
            for field in search_fields:
                annotations[f"{field}_headline"] = self.make_headline(field, search_query, search_type)
        else:
            for model in search_fields:
                for field in search_fields[model]:
                    annotations[f"{model}_{field}_headline"] = self.make_headline(f"{model}__{field}", search_query, search_type)
        return annotations

    def get_queryset(self):
        locations = self.request.GET.getlist("locations")
        categories = self.request.GET.getlist("categories")
        search_query = self.request.GET.get("q")
        sort_method = self.request.GET.get("sort")

        id_query = self.model.objects\
                       .filter(approved=True)\
                       .annotate(group_annotated=self.get_annotated_group())

        q_obj = self.get_location_filter(locations)
        if q_obj:
            id_query = id_query.filter(q_obj)

        if categories:
            id_query = id_query.filter(category__id__in=categories)

        if not search_query:
            id_query = id_query.order_by("group_annotated").distinct("group_annotated")

        annotations = {}
        ids = [i[0] for i in id_query.values_list("id", "group_annotated")]
        locations_prefetch = AbstractLocation.objects.all().select_subclasses()
        category_prefetch = AbstractCategory.objects.all().select_subclasses().select_related("subcategory__parent")\
                                            .contains_fr_docs()
        query = self.model.objects.filter(id__in=ids).select_subclasses().prefetch_related(
            Prefetch("locations", queryset=locations_prefetch),
            Prefetch("category", queryset=category_prefetch),
            Prefetch("related_resources", AbstractResource.objects.all().select_subclasses().prefetch_related(
                Prefetch("locations", queryset=locations_prefetch),
                Prefetch("category", queryset=category_prefetch),
            )),
        )

        if search_query:
            (search_type, cover_density) = (
                ("phrase", True)
                if search_query.startswith('"') and search_query.endswith('"')
                else ("plain", False)
            )
            annotations["rank"] = SearchRank(
                self.get_search_vectors(),
                SearchQuery(search_query, search_type=search_type, config="english"),
                cover_density=cover_density,
            )
            annotations = {**annotations, **self.get_search_headlines(search_query, search_type)}

        annotations["date_annotated"] = self.get_annotated_date()
        query = query.annotate(**annotations)
        query = query.filter(rank__gte=0.2) if search_query else query

        if search_query and sort_method == "relevance":
            return query.distinct().order_by("-rank")
        elif sort_method == "oldest":
            return query.distinct().order_by(F("date_annotated").asc(nulls_last=True))
        else:
            return query.order_by(F("date_annotated").desc(nulls_last=True)).distinct()


@extend_schema(
    description="Retrieve a list of all resources. "
                "Includes all types e.g. supplemental content, Federal Register Documents, etc. "
                "Searching is supported as well as inclusive filtering by title, part, subpart, and section. "
                "Results are paginated by default.",
    parameters=ResourceExplorerViewSetMixin.PARAMETERS,
    responses=AbstractResourceSerializer,
)
class AbstractResourceViewSet(ResourceExplorerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = AbstractResourcePolymorphicSerializer
    model = AbstractResource

    def get_annotated_date(self):
        return Case(
            When(supplementalcontent__isnull=False, then=F("supplementalcontent__date")),
            When(federalregisterdocument__isnull=False, then=F("federalregisterdocument__date")),
            default=None,
        )

    def get_annotated_group(self):
        return Case(
            When(federalregisterdocument__isnull=False, then=F("federalregisterdocument__group")),
            default=-1*F("pk"),
        )

    def get_search_fields(self):
        return {
            "supplementalcontent": ["name", "description"],
            "federalregisterdocument": ["name", "description", "document_number"],
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
        return ["name", "description"]


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

    @transaction.atomic
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
        return ["name", "description", "document_number"]

    def get_annotated_group(self):
        return F("group")


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
