from django.db.models import Prefetch
from rest_framework import viewsets
from drf_spectacular.utils import extend_schema

from resources.serializers import (
    PublicCategorySerializer,
    MetaCategorySerializer,
)

from resources.models import (
    PublicCategory,
    PublicSubCategory,
)


class PublicCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PublicCategorySerializer
    queryset = PublicCategory.objects.all().prefetch_related(
        Prefetch("subcategories", PublicSubCategory.objects.order_by("order")),
    ).order_by("order")


class InternalCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    pass
