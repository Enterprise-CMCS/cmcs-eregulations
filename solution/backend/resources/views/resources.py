from django.db.models import F, Prefetch, Q
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from common.mixins import ViewSetPagination
from resources.utils import get_citation_filter
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
)
from resources.serializers import (
    AbstractResourceSerializer,
    FederalRegisterLinkSerializer,
    InternalFileSerializer,
    InternalLinkSerializer,
    PublicLinkSerializer,
)

        # OpenApiQueryParameter("citations",
        #                       "Limit results to only resources linked to these CFR Citations. Use \"&citations=X&citations=Y\" "
        #                       "for multiple. Examples: 42, 42.433, 42.433.15, 42.433.D.", str, False),
class ResourceViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = ViewSetPagination
    serializer_class = AbstractResourceSerializer
    model = AbstractResource

    def get_queryset(self):
        citations = self.request.GET.getlist("citations")
        categories = self.request.GET.getlist("categories")
        subjects = self.request.GET.getlist("subjects")
        group_resources = self.request.GET.get("group_resources") or True

        query = self.model.objects.filter(approved=True).order_by(F("date").desc(nulls_last=True)).prefetch_related(
            Prefetch("category", AbstractCategory.objects.select_subclasses()),
            Prefetch("cfr_citations", AbstractCitation.objects.select_subclasses()),
            Prefetch("subjects", Subject.objects.all()),
            Prefetch("related_resources", AbstractResource.objects.select_subclasses().prefetch_related(
                Prefetch("cfr_citations", AbstractCitation.objects.select_subclasses()),
            )),
        )

        if group_resources:
            query = query.filter(Q(group_parent=True) | Q(related_resources__isnull=True)).filter(
                get_citation_filter(citations, "cfr_citations__") |
                get_citation_filter(citations, "related_resources__cfr_citations__")
            )

        # Filter by categories (both parent and subcategories) if the categories array is present
        if categories:
            query = query.filter(
                Q(category__pk__in=categories) |
                Q(category__abstractpubliccategory__publicsubcategory__parent__pk__in=categories) |
                Q(category__abstractinternalcategory__internalsubcategory__parent__pk__in=categories)
            )

        # Filter by subject pks if subjects array is present
        if subjects:
            query = query.filter(subjects__pk__in=subjects)

        # Filter out internal resources if the user is not logged in
        if not self.request.user.is_authenticated:
            prefix = "" if self.model == AbstractResource else "abstractresource_ptr__"
            query = query.filter(**{f"{prefix}abstractinternalresource__isnull": True})

        return query.distinct().select_subclasses()


class PublicResourceViewSet(ResourceViewSet):
    model = AbstractPublicResource


class PublicLinkViewSet(PublicResourceViewSet):
    model = PublicLink
    serializer_class = PublicLinkSerializer


class FederalRegisterLinkViewSet(PublicResourceViewSet):
    model = FederalRegisterLink
    serializer_class = FederalRegisterLinkSerializer


class FederalRegisterLinkDocumentNumberViewSet(viewsets.ReadOnlyModelViewSet):
    pass  # TODO: implement this endpoint


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
