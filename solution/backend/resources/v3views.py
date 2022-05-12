from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.core.exceptions import BadRequest
from django.db.models import Prefetch, Q, Case, When, F
from django.core.exceptions import BadRequest
from rest_framework.pagination import PageNumberPagination

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
)
from regcore.serializers import StringListSerializer


class ViewSetPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 1000
    page_size = 100


class OptionalPaginationMixin:
    paginate_by_default = True

    @property
    def pagination_class(self):
        paginate = self.request.GET.get(
            "paginate",
            "true" if self.paginate_by_default else "false"
        ).lower() == "true"
        return ViewSetPagination if paginate else None


class CategoryViewSet(OptionalPaginationMixin, viewsets.ReadOnlyModelViewSet):
    paginate_by_default = False
    queryset = AbstractCategory.objects.all().select_subclasses().select_related("subcategory__parent").order_by("order")
    serializer_class = AbstractCategoryPolymorphicSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["parent_details"] = self.request.GET.get("parent_details", "true")
        return context


class CategoryTreeViewSet(OptionalPaginationMixin, viewsets.ReadOnlyModelViewSet):
    paginate_by_default = False
    queryset = Category.objects.all().select_subclasses().prefetch_related(
        Prefetch("sub_categories", SubCategory.objects.all().order_by("order")),
    ).order_by("order")
    serializer_class = CategoryTreeSerializer


class LocationViewSet(OptionalPaginationMixin, viewsets.ModelViewSet):
    queryset = AbstractLocation.objects.all().select_subclasses()

    authentication_classes = [SettingsAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return AbstractLocationCreateSerializer
        return AbstractLocationPolymorphicSerializer


class ResourceExplorerViewSetMixin(OptionalPaginationMixin):
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

    def parse_locations(self, locations):
        queries = []
        for loc in locations:
            split = loc.split("-")
            length = len(split)

            if length < 1 or \
               (length >= 1 and not is_int(split[0])) or \
               (length >= 2 and (not is_int(split[0]) or not is_int(split[1]))):
                raise BadRequest(f"\"{loc}\" is not a valid title, part, section, or subpart!")

            q = Q(locations__title=split[0])
            if length > 1:
                q &= Q(locations__part=split[1])
                if length > 2:
                    q &= (
                        Q(locations__section__section_id=split[2])
                        if is_int(split[2])
                        else Q(locations__subpart__subpart_id=split[2])
                    )

            queries.append(q)
        return queries

    def get_queryset(self):
        query = self.model.objects.all().select_subclasses().prefetch_related(
            Prefetch("locations", AbstractLocation.objects.all().select_subclasses()),
            Prefetch("category", AbstractCategory.objects.all().select_subclasses().select_related("subcategory__parent")),
        )

        locations = self.request.GET.getlist("locations")
        categories = self.request.GET.getlist("categories")
        search_query = self.request.GET.get("q")

        q_queries = self.parse_locations(locations)
        if q_queries:
            q_obj = q_queries[0]
            for q in q_queries[1:]:
                q_obj |= q
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


class AbstractResourceViewSet(ResourceExplorerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = AbstractResourcePolymorphicSerializer
    model = AbstractResource

    def compute_dates(self, query):
        return query.annotate(date_annotated=Case(
            When(
                supplementalcontent__isnull=False,
                then=F("supplementalcontent__date"),
            ),
            When(
                federalregisterdocument__isnull=False,
                then=F("federalregisterdocument__date"),
            ),
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


class FederalRegisterDocsNumberViewSet(OptionalPaginationMixin, viewsets.ReadOnlyModelViewSet):
    paginate_by_default = False
    queryset = FederalRegisterDocument.objects.all().values_list("document_number", flat=True).distinct()
    serializer_class = StringListSerializer
