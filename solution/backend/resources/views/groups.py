from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from cmcs_regulations.utils import ViewSetPagination
from resources.models import (
    AbstractCategory,
    AbstractCitation,
    AbstractPublicResource,
    AbstractResource,
    ResourceGroup,
    Subject,
)
from resources.serializers import ResourceGroupSerializer


@extend_schema(
    tags=["resources/metadata"],
    description="Retrieve a list of resource groups, which are collections of related resources. "
                "This endpoint supports both authenticated and unauthenticated users, with different "
                "resource filters applied based on the user's authentication status. Authenticated users "
                "can access all resources, while unauthenticated users are limited to public resources only. "
                "The results include prefetched resources belonging to each group.",
    responses={200: ResourceGroupSerializer(many=True)},
)
class ResourceGroupViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ResourceGroupSerializer
    pagination_class = ViewSetPagination

    def get_queryset(self):
        resource_filter = (AbstractResource
                           if self.request.user.is_authenticated else
                           AbstractPublicResource).objects.select_subclasses()
        return ResourceGroup.objects.prefetch_related(
            Prefetch("resources", queryset=resource_filter.prefetch_related(
                Prefetch("category", AbstractCategory.objects.select_subclasses()),
                Prefetch("cfr_citations", AbstractCitation.objects.select_subclasses()),
                Prefetch("subjects", Subject.objects.all()),
            )),
        )
