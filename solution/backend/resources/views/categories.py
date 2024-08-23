from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from common.mixins import ViewSetPagination
from resources.models import (
    InternalCategory,
    InternalSubCategory,
    PublicCategory,
    PublicSubCategory,
)
from resources.serializers import (
    InternalCategoryWithSubCategoriesSerializer,
    PublicCategoryWithSubCategoriesSerializer,
)

@extend_schema(
    description="Retrieve a list of public categories along with their subcategories. "
                "This endpoint provides access to categories that are publicly available. "
                "Categories and their respective subcategories are ordered based on their "
                "defined order field."
)
class PublicCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = ViewSetPagination
    serializer_class = PublicCategoryWithSubCategoriesSerializer
    queryset = PublicCategory.objects.all().prefetch_related(
        Prefetch("subcategories", PublicSubCategory.objects.order_by("order")),
    ).order_by("order")

@extend_schema(
    description="Retrieve a list of internal categories along with their subcategories. "
                "This endpoint is accessible only to authenticated users and provides access "
                "to internal categories that may include restricted or confidential information. "
                "Categories and their respective subcategories are ordered based on their "
                "defined order field."
)
class InternalCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = ViewSetPagination
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = InternalCategoryWithSubCategoriesSerializer
    queryset = InternalCategory.objects.all().prefetch_related(
        Prefetch("subcategories", InternalSubCategory.objects.order_by("order")),
    ).order_by("order")
