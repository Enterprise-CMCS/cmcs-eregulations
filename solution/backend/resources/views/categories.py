from django.db.models import Prefetch
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from drf_spectacular.utils import extend_schema

from resources.serializers import (
    PublicCategorySerializer,
    MetaCategorySerializer,
    InternalCategorySerializer,
)

from resources.models import (
    PublicCategory,
    PublicSubCategory,
    InternalCategory,
    InternalSubCategory,
)


class PublicCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PublicCategorySerializer
    queryset = PublicCategory.objects.all().prefetch_related(
        Prefetch("subcategories", PublicSubCategory.objects.order_by("order")),
    ).order_by("order")


class InternalCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = InternalCategorySerializer
    queryset = InternalCategory.objects.all().prefetch_related(
        Prefetch("subcategories", InternalSubCategory.objects.order_by("order")),
    ).order_by("order")
