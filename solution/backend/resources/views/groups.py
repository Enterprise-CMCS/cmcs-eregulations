from django.db.models import Prefetch
from rest_framework import viewsets

from common.mixins import ViewSetPagination

from resources.models import (
    AbstractPublicResource,
    AbstractResource,
    ResourceGroup,
)
from resources.serializers import ResourceGroupSerializer


class ResourceGroupViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ResourceGroupSerializer
    pagination_class = ViewSetPagination

    def get_queryset(self):
        resource_filter = (AbstractResource
                           if self.request.user.is_authenticated else
                           AbstractPublicResource).objects.select_subclasses()
        return ResourceGroup.objects.prefetch_related(
            Prefetch("resources", queryset=resource_filter),
        )
