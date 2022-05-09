from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.core.exceptions import BadRequest
from django.db.models import Prefetch, Q
from django.core.exceptions import BadRequest

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

from .views import SettingsAuthentication

from .v3serializers import (
    FederalRegisterDocumentCreateSerializer,
    AbstractCategoryPolymorphicSerializer,
    AbstractLocationPolymorphicSerializer,
    AbstractResourcePolymorphicSerializer,
    SupplementalContentSerializer,
)
from regcore.serializers import StringListSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AbstractCategory.objects.all().select_subclasses().select_related("subcategory__parent")
    serializer_class = AbstractCategoryPolymorphicSerializer


class LocationViewSet(viewsets.ModelViewSet):
    queryset = AbstractLocation.objects.all().select_subclasses()
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return AbstractLocationCreateSerializer
        return AbstractLocationPolymorphicSerializer


class AbstractResourceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AbstractResourcePolymorphicSerializer
    model = AbstractResource

    def get_search_fields(self):
        return [
            ("supplementalcontent__name", "A"),
            ("supplementalcontent__description", "A"),
            ("federalregisterdocument__name", "A"),
            ("federalregisterdocument__description", "A"),
            ("federalregisterdocument__docket_number", "A"),
            ("federalregisterdocument__document_number", "A"),
        ]

    def get_search_map(self):
        fields = {}
        for i in self.get_search_fields():
            fields[f"{i[0]}_headline"] = f"{i[0]}_headline"
        return fields

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["search_map"] = self.get_search_map()
        return context

    def get_search_vectors(self):
        fields = self.get_search_fields()
        v = SearchVector(fields[0][0], weight=fields[0][1], config="english")
        for i in fields[1:]:
            v += SearchVector(i[0], weight=i[1], config="english")
        return v
    
    def get_search_headlines(self, search_query, search_type):
        fields = self.get_search_fields()
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

        return query


class SupplementalContentViewSet(AbstractResourceViewSet):
    serializer_class = SupplementalContentSerializer
    model = SupplementalContent

    def get_search_fields(self):
        return [
            ("name", "A"),
            ("description", "A"),
        ]
    
    def get_search_map(self):
        return {
            "supplementalcontent__name_headline": "name_headline",
            "supplementalcontent__description_headline": "description_headline",
        }

class FederalRegisterDocsViewSet(viewsets.ModelViewSet):
    queryset = FederalRegisterDocument.objects.all().values_list("document_number", flat=True).distinct()

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
        return StringListSerializer
