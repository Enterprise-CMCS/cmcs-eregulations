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
    queryset = AbstractResource.objects.all().select_subclasses().prefetch_related(
        Prefetch("locations", AbstractLocation.objects.all().select_subclasses()),
        Prefetch("category", AbstractCategory.objects.all().select_subclasses().select_related("subcategory__parent")),
    )

    serializer_class = AbstractResourcePolymorphicSerializer

    def parse_locations(self, locations):
        titles = []
        parts = []
        sections = []
        subparts = []

        for loc in locations:
            split = loc.split("-")
            length = len(split)
            
            if length < 1 or \
               (length >= 1 and not is_int(split[0])) or \
               (length >= 2 and (not is_int(split[0]) or not is_int(split[1]))):
                raise BadRequest(f"\"{loc}\" is not a valid title, part, section, or subpart!")
            
            if length == 1 and split[0] not in titles:
                titles.append(split[0])
            elif length == 2 and (split[0], split[1]) not in parts:
                parts.append((split[0], split[1]))
            elif length == 3:
                l = (split[0], split[1], split[2])
                (sections if is_int(l[2]) else subparts).append(l)
        
        return (titles, parts, sections, subparts)

    def get_queryset(self):
        query = super().get_queryset()

        locations = self.request.GET.getlist("locations")
        categories = self.request.GET.getlist("categories")
        search_query = self.request.GET.get("q")

        (titles, parts, sections, subparts) = self.parse_locations(locations)

        q_queries = []
        if titles:
            q_queries.append(Q(locations__title__in=titles))
        for p in parts:
            q_queries.append(Q(locations__title=p[0]) & Q(locations__part=p[1]))

        q_obj = q_queries[0] if q_queries else None
        if q_obj:
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
