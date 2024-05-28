from django.db.models import Prefetch, Q, Count, Value
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from drf_spectacular.utils import extend_schema

from resources.serializers import (
    ResourceGroupSerializer
)

from resources.models import (
    ResourceGroup,
    NewAbstractResource,
    AbstractPublicResource,
)


class ResourceGroupViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ResourceGroupSerializer
    
    def get_queryset(self):
        resource_filter = (NewAbstractResource
                           if self.request.user.is_authenticated else
                           AbstractPublicResource).objects.select_subclasses()
        return ResourceGroup.objects.prefetch_related(
            Prefetch("resources", queryset=resource_filter),
        )
