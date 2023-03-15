from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db import transaction
from django.db.models import Case, When, F
from django.http import JsonResponse

from .mixins import ResourceExplorerViewSetMixin, FRDocGroupingMixin
from common.mixins import OptionalPaginationMixin, PAGINATION_PARAMS

from resources.models import (
    AbstractResource,
    SupplementalContent,
    FederalRegisterDocument,
)

from resources.serializers.resources import (
    AbstractResourcePolymorphicSerializer,
    SupplementalContentSerializer,
    FederalRegisterDocumentCreateSerializer,
    FederalRegisterDocumentSerializer,
    StringListSerializer,
    MetaResourceSerializer,
)

from common.auth import SettingsAuthentication


@extend_schema(
    description="Retrieve a list of all resources. "
                "Includes all types e.g. supplemental content, Federal Register Documents, etc. "
                "Searching is supported as well as inclusive filtering by title, part, subpart, and section. "
                "Results are paginated by default.",
    parameters=ResourceExplorerViewSetMixin.PARAMETERS,
    responses=MetaResourceSerializer.many(True),
)
class AbstractResourceViewSet(FRDocGroupingMixin, ResourceExplorerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = AbstractResourcePolymorphicSerializer
    model = AbstractResource

    def get_annotated_date(self):
        return Case(
            When(supplementalcontent__isnull=False, then=F("supplementalcontent__date")),
            When(federalregisterdocument__isnull=False, then=F("federalregisterdocument__date")),
            default=None,
        )

    def get_annotated_name_sort(self):
        return Case(
            When(supplementalcontent__isnull=False, then=F("supplementalcontent__name_sort")),
            When(federalregisterdocument__isnull=False, then=F("federalregisterdocument__name_sort")),
            default=None,
        )

    def get_annotated_description_sort(self):
        return Case(
            When(supplementalcontent__isnull=False, then=F("supplementalcontent__description_sort")),
            When(federalregisterdocument__isnull=False, then=F("federalregisterdocument__description_sort")),
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


class FederalRegisterDocsViewSet(FRDocGroupingMixin, ResourceExplorerViewSetMixin, viewsets.ModelViewSet):
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
        sc = self.get_serializer(frdoc, data=data, context={**self.get_serializer_context(), **{"created": created}})
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
