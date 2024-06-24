from django.db.models import F, Prefetch, Q
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from common.mixins import (
    CitationFiltererMixin,
    ViewSetPagination,
)
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


class ResourceViewSet(CitationFiltererMixin, viewsets.ReadOnlyModelViewSet):
    citation_filter_prefix = "cfr_citations__"
    pagination_class = ViewSetPagination
    serializer_class = AbstractResourceSerializer
    model = AbstractResource

    def get_queryset(self):
        citations = self.request.GET.getlist("citations")
        categories = self.request.GET.getlist("categories")
        subjects = self.request.GET.getlist("subjects")

        query = self.model.objects.order_by(F("date").desc(nulls_last=True)).prefetch_related(
            Prefetch("category", AbstractCategory.objects.select_subclasses()),
            Prefetch("cfr_citations", AbstractCitation.objects.select_subclasses()),
            Prefetch("subjects", Subject.objects.all()),
        )

        # Filter inclusively by citations if this array exists
        citation_filter = self.get_citation_filter(citations)
        if citation_filter:
            query = query.filter(citation_filter)

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
            query = query.filter(abstractresource_ptr__abstractinternalresource__isnull=True)

        return query.select_subclasses()


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
