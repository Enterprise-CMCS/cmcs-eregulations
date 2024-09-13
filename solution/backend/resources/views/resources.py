import logging

from django.db import transaction
from django.db.models import F, Prefetch, Q
from django.http import JsonResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from cmcs_regulations.utils import ViewSetPagination
from common.auth import SettingsAuthentication
from resources.models import (
    AbstractCategory,
    AbstractCitation,
    AbstractInternalResource,
    AbstractPublicResource,
    AbstractResource,
    FederalRegisterLink,
    InternalFile,
    InternalLink,
    PublicLink,
    ResourcesConfiguration,
    Subject,
)
from resources.serializers import (
    AbstractResourceSerializer,
    FederalRegisterLinkCreateSerializer,
    FederalRegisterLinkSerializer,
    InternalFileSerializer,
    InternalLinkSerializer,
    PublicLinkSerializer,
    StringListSerializer,
)
from resources.utils import (
    call_text_extractor,
    get_citation_filter,
    string_to_bool,
)

logger = logging.getLogger(__name__)

# OpenApiQueryParameter("citations",
#                       "Limit results to only resources linked to these CFR Citations. Use \"&citations=X&citations=Y\" "
#                       "for multiple. Examples: 42, 42.433, 42.433.15, 42.433.D.", str, False),


class ResourceCountPagination(ViewSetPagination):
    def get_count_map(self):
        prefix = "" if self.view.model == AbstractResource else "abstractresource_ptr__"
        internal_filter = Q(**{f"{prefix}abstractinternalresource__isnull": False})
        public_filter = Q(**{f"{prefix}abstractpublicresource__isnull": False})
        return [
            {"name": "internal_count", "count_field": "pk", "filter": internal_filter},
            {"name": "public_count", "count_field": "pk", "filter": public_filter},
        ]


COMMON_QUERY_PARAMETERS = [
    OpenApiParameter(
        name="citations",
        type=OpenApiTypes.STR,  # Assuming citations are strings, use OpenApiTypes.INT if they're integers
        location=OpenApiParameter.QUERY,
        description="Limit results to only resources linked to these citations. Use \"&citations=X&citations=Y\" "
                    "for multiple. Examples: 42, 42.433, 42.433.15, 42.433.D",
        required=False,
        explode=False,  # Treat as an array, not a CSV string
    ),
    OpenApiParameter(
        name="categories",
        type=OpenApiTypes.STR,  # Assuming categories are strings, use OpenApiTypes.INT if they're integers
        location=OpenApiParameter.QUERY,
        description="List of category IDs to filter by, including subcategories",
        required=False,
        explode=False,
    ),
    OpenApiParameter(
        name="subjects",
        type=OpenApiTypes.STR,  # Assuming subjects are strings, use OpenApiTypes.INT if they're integers
        location=OpenApiParameter.QUERY,
        description="List of subject IDs to filter by. Use \"&subjects=1&subjects=2\""
                    " for multiple.",
        required=False,
        explode=False,
    ),
    OpenApiParameter(
        name="group_resources",
        type=OpenApiTypes.BOOL,
        location=OpenApiParameter.QUERY,
        description="Boolean flag to control resource grouping",
        required=False,
        default=True,
    ),
]


@extend_schema(parameters=COMMON_QUERY_PARAMETERS)
class ResourceViewSet(viewsets.ModelViewSet):
    pagination_class = ResourceCountPagination
    serializer_class = AbstractResourceSerializer
    model = AbstractResource

    @extend_schema(
        description="Retrieve, filter, and group various resources based on citations, "
                    "categories, subjects, and other criteria. This endpoint allows "
                    "authenticated and unauthenticated users to view approved "
                    "resources, with options to group resources and filter by related fields "
                    "such as categories, subjects, and citations.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_context(self):
        return {"show_related": string_to_bool(self.request.GET.get("group_resources"), True)}

    def get_queryset(self):
        citations = self.request.GET.getlist("citations")
        categories = self.request.GET.getlist("categories")
        subjects = self.request.GET.getlist("subjects")
        group_resources = string_to_bool(self.request.GET.get("group_resources"), True)

        category_prefetch = AbstractCategory.objects.select_subclasses()
        citation_prefetch = AbstractCitation.objects.select_subclasses()
        subject_prefetch = Subject.objects.all()

        query = self.model.objects.filter(approved=True).order_by(F("date").desc(nulls_last=True)).prefetch_related(
            Prefetch("category", category_prefetch),
            Prefetch("cfr_citations", citation_prefetch),
            Prefetch("subjects", subject_prefetch),
        )

        # Filter out internal resources if the user is not logged in
        if not self.request.user.is_authenticated:
            prefix = "" if self.model == AbstractResource else "abstractresource_ptr__"
            query = query.filter(**{f"{prefix}abstractinternalresource__isnull": True})

        if group_resources:
            # Prefetch related_resources and filter out non-parent group members
            query = query.prefetch_related(
                Prefetch("related_resources", AbstractResource.objects.filter(approved=True).prefetch_related(
                    Prefetch("category", category_prefetch),
                    Prefetch("cfr_citations", citation_prefetch),
                    Prefetch("subjects", subject_prefetch),
                ).order_by(F("date").desc(nulls_last=True)).select_subclasses()),
            ).filter(Q(group_parent=True) | Q(related_resources__isnull=True))
            citation_prefix = "related_citations__"
            category_prefix = "related_categories__"
            subject_prefix = "related_subjects__"
        else:
            citation_prefix = "cfr_citations__"
            category_prefix = "category__"
            subject_prefix = "subjects__"

        # Filter by citations
        query = query.filter(get_citation_filter(citations, citation_prefix))

        # Filter by categories (both parent and subcategories) if the categories array is present
        if categories:
            query = query.filter(
                Q(**{f"{category_prefix}pk__in": categories}) |
                Q(**{f"{category_prefix}abstractpubliccategory__publicsubcategory__parent__pk__in": categories}) |
                Q(**{f"{category_prefix}abstractinternalcategory__internalsubcategory__parent__pk__in": categories})
            )

        # Filter by subject pks if subjects array is present
        if subjects:
            query = query.filter(**{f"{subject_prefix}pk__in": subjects})

        return query.distinct().select_subclasses()


@extend_schema(description="Retrieve a list of public resources with optional filtering by "
                           "citations, categories, subjects, and resource grouping.")
class PublicResourceViewSet(ResourceViewSet):
    model = AbstractPublicResource


@extend_schema(description="Retrieve a list of public links, including options to filter by citations, "
                           "categories, subjects, and grouping criteria. This endpoint is available to "
                           "all users.")
class PublicLinkViewSet(PublicResourceViewSet):
    model = PublicLink
    serializer_class = PublicLinkSerializer


@extend_schema(description="Retrieve and update Federal Register links. "
                           "This endpoint allows filtering by citations, "
                           "categories, subjects, and grouping criteria. "
                           "Only authenticated users can update existing Federal "
                           "Register links.")
class FederalRegisterLinkViewSet(PublicResourceViewSet):
    model = FederalRegisterLink
    authentication_classes = [SettingsAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return FederalRegisterLinkCreateSerializer
        return FederalRegisterLinkSerializer

    @transaction.atomic
    @extend_schema(description="Upload a Federal Register Document to the eRegs Resources system. "
                               "If the document already exists, it will be updated.")
    def update(self, request, **kwargs):
        data = request.data
        link, created = FederalRegisterLink.objects.get_or_create(document_number=data["document_number"])
        data["id"] = link.pk
        sc = self.get_serializer(link, data=data, context={**self.get_serializer_context(), **{"created": created}})
        sc.is_valid(raise_exception=True)
        sc.save()
        if ResourcesConfiguration.get_solo().auto_extract:
            _, fail = call_text_extractor(request, FederalRegisterLink.objects.filter(pk=link.pk))
            if fail:
                logger.warning("Failed to extract text for Federal Register Link %i: %s", link.pk, fail[0]["reason"])
        return JsonResponse(sc.validated_data)


class InternalResourceViewSet(ResourceViewSet):
    model = AbstractInternalResource
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(description="Retrieve a list of internal resources, including both "
                               "internal files and internal links, which are only accessible "
                               "to authenticated users. This endpoint supports options to "
                               "group resources and filter by citations, categories, and subjects.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema(description="Retrieve a list of internal files, which are only"
                           "accessible to authenticated users. This endpoint "
                           "supports options to group resources and filter by "
                           "citations, categories, and subjects.")
class InternalFileViewSet(InternalResourceViewSet):
    model = InternalFile
    serializer_class = InternalFileSerializer


@extend_schema(description="Retrieve a list of internal links, which are "
                           "only accessible to authenticated users. This "
                           "endpoint supports options to group resources "
                           "and filter by citations, categories, and subjects.")
class InternalLinkViewSet(InternalResourceViewSet):
    model = InternalLink
    serializer_class = InternalLinkSerializer


@extend_schema(description="Retrieve a distinct list of Federal Register document numbers. "
                           "This endpoint is read-only and returns a list of unique document numbers")
class FederalRegisterLinksNumberViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FederalRegisterLink.objects.all().values_list("document_number", flat=True).distinct()
    serializer_class = StringListSerializer
