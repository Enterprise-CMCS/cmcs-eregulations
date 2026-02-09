import logging

from django.apps import apps
from django.db import transaction
from django.db.models import F, Prefetch, Q
from django.http import JsonResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from cmcs_regulations.utils import ViewSetPagination
from common.auth import SettingsAuthentication
from regulations.utils import LinkConfigMixin, LinkConversionsMixin
from resources.models import (
    AbstractCategory,
    AbstractCitation,
    AbstractInternalResource,
    AbstractPublicResource,
    AbstractResource,
    Act,
    FederalRegisterLink,
    InternalFile,
    InternalLink,
    PublicLink,
    StatuteCitation,
    Subject,
    UscCitation,
)
from resources.serializers import (
    AbstractResourceSerializer,
    FederalRegisterLinkCreateSerializer,
    FederalRegisterLinkSerializer,
    InternalFileSerializer,
    InternalLinkSerializer,
    MetaInternalResourceSerializer,
    MetaPublicResourceSerializer,
    MetaResourceSerializer,
    PublicLinkSerializer,
    StringListSerializer,
)
from resources.utils import (
    ACT_CITATION_FILTER_PARAMETER,
    CITATION_FILTER_PARAMETER,
    USC_CITATION_FILTER_PARAMETER,
    get_act_citation_filter,
    get_citation_filter,
    get_usc_citation_filter,
    string_to_bool,
)

logger = logging.getLogger(__name__)


class ResourceCountPagination(ViewSetPagination):
    def get_additional_attributes(self):
        try:
            from content_search.views import ContentCountViewSet
            return {**super().get_additional_attributes(), **{
                "count_url": ContentCountViewSet.generate_url(self.request),
            }}
        except ImportError:
            return super().get_additional_attributes()

    def get_additional_attribute_schemas(self):
        try:
            from content_search.views import ContentCountViewSet  # noqa
            return {**super().get_additional_attribute_schemas(), **{
                "count_url": {
                    "type": "string",
                    "format": "uri",
                    "nullable": True,
                    "example": "http://api.example.org/content_count/?q=example",
                },
            }}
        except ImportError:
            return super().get_additional_attribute_schemas()


RESOURCE_ENDPOINT_PARAMETERS = [
    CITATION_FILTER_PARAMETER,
    ACT_CITATION_FILTER_PARAMETER,
    USC_CITATION_FILTER_PARAMETER,
    OpenApiParameter(
        name="categories",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description="List of category/subcategory object IDs to filter by. "
                    "Use \"&categories=1&categories=2\" for multiple.",
        required=False,
        explode=True,
    ),
    OpenApiParameter(
        name="subjects",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description="List of subject IDs to filter by. "
                    "Use \"&subjects=1&subjects=2\" for multiple.",
        required=False,
        explode=True,
    ),
    OpenApiParameter(
        name="group_resources",
        type=OpenApiTypes.BOOL,
        location=OpenApiParameter.QUERY,
        description="Set to \"true\" to group related resources together under the \"related_resources\" field. "
                    "Set to \"false\" to disable grouping.",
        required=False,
        default=True,
    ),
] + ViewSetPagination.QUERY_PARAMETERS


class ResourceViewSet(LinkConfigMixin, LinkConversionsMixin, viewsets.ModelViewSet):
    pagination_class = ResourceCountPagination
    serializer_class = AbstractResourceSerializer
    model = AbstractResource

    @extend_schema(
        tags=["resources"],
        description="Retrieve, filter, and group various resources based on citations, "
                    "categories, subjects, and other criteria. This endpoint allows "
                    "authenticated and unauthenticated users to view approved "
                    "resources, with options to group resources and filter by related fields "
                    "such as categories, subjects, and citations.",
        parameters=RESOURCE_ENDPOINT_PARAMETERS,
        responses={200: MetaResourceSerializer.many(True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["show_related"] = string_to_bool(self.request.GET.get("group_resources"), True)
        return context

    def get_queryset(self):
        citations = self.request.GET.getlist("citations")
        act_citations = self.request.GET.getlist("act_citations")
        usc_citations = self.request.GET.getlist("usc_citations")
        categories = self.request.GET.getlist("categories")
        subjects = self.request.GET.getlist("subjects")
        group_resources = string_to_bool(self.request.GET.get("group_resources"), True)

        citation_prefetch = AbstractCitation.objects.select_subclasses()
        statute_citation_prefetch = StatuteCitation.objects.prefetch_related(
            Prefetch("act", Act.objects.all()),
        )
        usc_citation_prefetch = UscCitation.objects.all()
        subject_prefetch = Subject.objects.all()
        category_prefetch = AbstractCategory.objects.select_subclasses().prefetch_related(
            Prefetch("parent", AbstractCategory.objects.select_subclasses()),
        )

        query = self.model.objects.filter(approved=True).order_by(F("date").desc(nulls_last=True)).prefetch_related(
            Prefetch("category", category_prefetch),
            Prefetch("cfr_citations", citation_prefetch),
            Prefetch("act_citations", statute_citation_prefetch),
            Prefetch("usc_citations", usc_citation_prefetch),
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
                    Prefetch("act_citations", statute_citation_prefetch),
                    Prefetch("usc_citations", usc_citation_prefetch),
                    Prefetch("subjects", subject_prefetch),
                ).order_by(F("date").desc(nulls_last=True)).select_subclasses()),
            ).filter(Q(group_parent=True) | Q(related_resources__isnull=True))
            citation_prefix = "related_citations__"
            act_citation_prefix = "related_act_citations__"
            usc_citation_prefix = "related_usc_citations__"
            category_prefix = "related_categories__"
            subject_prefix = "related_subjects__"
        else:
            citation_prefix = "cfr_citations__"
            act_citation_prefix = "act_citations__"
            usc_citation_prefix = "usc_citations__"
            category_prefix = "category__"
            subject_prefix = "subjects__"

        # Filter by citations
        query = query.filter(get_citation_filter(citations, citation_prefix))
        query = query.filter(get_act_citation_filter(act_citations, act_citation_prefix))
        query = query.filter(get_usc_citation_filter(usc_citations, usc_citation_prefix))

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


class PublicResourceViewSet(ResourceViewSet):
    model = AbstractPublicResource

    @extend_schema(
        tags=["resources"],
        description="Retrieve a list of public resources, including options to filter by citations, "
                    "categories, subjects, and grouping criteria. This endpoint is available to all users.",
        parameters=RESOURCE_ENDPOINT_PARAMETERS,
        responses={200: MetaPublicResourceSerializer.many(True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PublicLinkViewSet(PublicResourceViewSet):
    model = PublicLink
    serializer_class = PublicLinkSerializer

    @extend_schema(
        tags=["resources"],
        description="Retrieve a list of public links, including options to filter by citations, "
                    "categories, subjects, and grouping criteria. This endpoint is available to all users.",
        parameters=RESOURCE_ENDPOINT_PARAMETERS,
        responses={200: PublicLinkSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FederalRegisterLinkViewSet(PublicResourceViewSet):
    model = FederalRegisterLink
    authentication_classes = [SettingsAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return FederalRegisterLinkCreateSerializer
        return FederalRegisterLinkSerializer

    @extend_schema(
        tags=["resources"],
        description="Retrieve a list of Federal Register links, including options to filter by citations, "
                    "categories, subjects, and grouping criteria. This endpoint is available to all users.",
        parameters=RESOURCE_ENDPOINT_PARAMETERS,
        responses={200: FederalRegisterLinkSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @transaction.atomic
    @extend_schema(
        tags=["resources"],
        description="Upload a Federal Register link to the eRegs Resources system. "
                    "If the document already exists, it will be updated.",
        request=FederalRegisterLinkCreateSerializer,
        responses={200: FederalRegisterLinkSerializer},
    )
    def update(self, request, **kwargs):
        data = request.data
        link, created = FederalRegisterLink.objects.get_or_create(document_number=data["document_number"])
        data["id"] = link.pk
        sc = self.get_serializer(link, data=data, context={**self.get_serializer_context(), **{"created": created}})
        sc.is_valid(raise_exception=True)
        sc.save()

        # If content search is installed, run the text extractor
        if apps.is_installed("content_search"):
            from content_search.models import ContentSearchConfiguration
            from content_search.utils import call_text_extractor_for_resources
            if ContentSearchConfiguration.get_solo().auto_extract:
                _, fail = call_text_extractor_for_resources(request, FederalRegisterLink.objects.filter(pk=link.pk))
                if fail:
                    logger.warning("Failed to extract text for Federal Register Link %i: %s", link.pk, fail[0]["reason"])

        return JsonResponse(sc.validated_data)


class InternalResourceViewSet(ResourceViewSet):
    model = AbstractInternalResource
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["resources"],
        description="Retrieve a list of internal resources, including both internal files and internal links, "
                    "which are only accessible to authenticated users. This endpoint supports options to group "
                    "resources and filter by citations, categories, and subjects.",
        parameters=RESOURCE_ENDPOINT_PARAMETERS,
        responses={200: MetaInternalResourceSerializer.many(True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class InternalFileViewSet(InternalResourceViewSet):
    model = InternalFile
    serializer_class = InternalFileSerializer

    @extend_schema(
        tags=["resources"],
        description="Retrieve a list of internal files, which are only accessible to authenticated users. "
                    "This endpoint supports options to group resources and filter by citations, categories, and subjects.",
        parameters=RESOURCE_ENDPOINT_PARAMETERS,
        responses={200: InternalFileSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class InternalLinkViewSet(InternalResourceViewSet):
    model = InternalLink
    serializer_class = InternalLinkSerializer

    @extend_schema(
        tags=["resources"],
        description="Retrieve a list of internal links, which are only accessible to authenticated users. "
                    "This endpoint supports options to group resources and filter by citations, categories, and subjects.",
        parameters=RESOURCE_ENDPOINT_PARAMETERS,
        responses={200: InternalLinkSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FederalRegisterLinksNumberViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FederalRegisterLink.objects.all().values_list("document_number", flat=True).distinct()
    serializer_class = StringListSerializer

    @extend_schema(
        tags=["resources"],
        description="Retrieve a list of Federal Register document numbers. "
                    "This endpoint is read-only and returns a list of unique document numbers.",
        responses={(200, "application/json"): {"type": "string"}},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
