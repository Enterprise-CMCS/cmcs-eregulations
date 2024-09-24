from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from cmcs_regulations.utils import ViewSetPagination
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
    tags=["resources/metadata"],
    description="Retrieve a list of public categories along with their subcategories. "
                "This endpoint provides access to categories that are publicly available. "
                "Categories and their respective subcategories are ordered based on their "
                "defined order field.",
    responses={200: PublicCategoryWithSubCategoriesSerializer(many=True)},
)
class PublicCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = ViewSetPagination
    serializer_class = PublicCategoryWithSubCategoriesSerializer
    queryset = PublicCategory.objects.all().prefetch_related(
        Prefetch("subcategories", PublicSubCategory.objects.order_by("order")),
    ).order_by("order")


@extend_schema(
    tags=["resources/metadata"],
    description="Retrieve a list of internal categories along with their subcategories. "
                "This endpoint is accessible only to authenticated users and provides access "
                "to internal categories that may include restricted or confidential information. "
                "Categories and their respective subcategories are ordered based on their "
                "defined order field.",
    responses={200: InternalCategoryWithSubCategoriesSerializer(many=True)},
)
class InternalCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = ViewSetPagination
    permission_classes = [IsAuthenticated]
    serializer_class = InternalCategoryWithSubCategoriesSerializer
    queryset = InternalCategory.objects.all().prefetch_related(
        Prefetch("subcategories", InternalSubCategory.objects.order_by("order")),
    ).order_by("order")
