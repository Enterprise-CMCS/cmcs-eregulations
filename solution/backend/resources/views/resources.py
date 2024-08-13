import logging

from django.db import transaction
from django.db.models import F, Prefetch, Q
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from common.mixins import ViewSetPagination
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
    Subject,
    ResourcesConfiguration,
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
    get_citation_filter,
    string_to_bool,
    call_text_extractor,
)

logger = logging.getLogger(__name__)


# OpenApiQueryParameter("citations",
#                       "Limit results to only resources linked to these CFR Citations. Use \"&citations=X&citations=Y\" "
#                       "for multiple. Examples: 42, 42.433, 42.433.15, 42.433.D.", str, False),
class ResourceViewSet(viewsets.ModelViewSet):
    pagination_class = ViewSetPagination
    serializer_class = AbstractResourceSerializer
    model = AbstractResource

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
                ).select_subclasses()),
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


class PublicResourceViewSet(ResourceViewSet):
    model = AbstractPublicResource


class PublicLinkViewSet(PublicResourceViewSet):
    model = PublicLink
    serializer_class = PublicLinkSerializer


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
                logger.warning(f"Failed to extract text for Federal Register Link {link.pk}: {fail[0]['reason']}")
        return JsonResponse(sc.validated_data)


class InternalResourceViewSet(ResourceViewSet):
    model = AbstractInternalResource
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]


class InternalFileViewSet(InternalResourceViewSet):
    model = InternalFile
    serializer_class = InternalFileSerializer


class InternalLinkViewSet(InternalResourceViewSet):
    model = InternalLink
    serializer_class = InternalLinkSerializer


class FederalRegisterLinksNumberViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FederalRegisterLink.objects.all().values_list("document_number", flat=True).distinct()
    serializer_class = StringListSerializer
