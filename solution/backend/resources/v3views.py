from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.core.exceptions import BadRequest
from django.db.models import Prefetch, Q
from django.core.exceptions import BadRequest

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
    queryset = AbstractResource.objects.all().select_subclasses().prefetch_related(
        Prefetch("locations", AbstractLocation.objects.all().select_subclasses()),
        Prefetch("category", AbstractCategory.objects.all().select_subclasses().select_related("subcategory__parent")),
    )

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
        query = super().get_queryset()

        locations = self.request.GET.getlist("locations")
        categories = self.request.GET.getlist("categories")
        search_query = self.request.GET.get("q")

        q_queries = self.parse_locations(locations)
        if q_queries:
            q_obj = q_queries[0]
            for q in q_queries[1:]:
                q_obj |= q
            query = query.filter(q_obj)

        return query


class SupplementalContentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SupplementalContent.objects.all()


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
