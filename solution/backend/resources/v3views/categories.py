from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, PolymorphicProxySerializer
from django.db.models import Prefetch

from .mixins import OptionalPaginationMixin, OpenApiQueryParameter, PAGINATION_PARAMS

from resources.models import (
    AbstractCategory,
    Category,
    SubCategory,
)

from resources.v3serializers.categories import (
    CategorySerializer,
    SubCategorySerializer,
    AbstractCategoryPolymorphicSerializer,
    CategoryTreeSerializer,
)


@extend_schema(
    description="Retrieve a flat list of all categories. Pagination is disabled by default.",
    parameters=OptionalPaginationMixin.PARAMETERS + PAGINATION_PARAMS + [
        OpenApiQueryParameter("parent_details", "Show details about each sub-category's parent, rather "
                              "than just the ID.", bool, False),
    ],
    responses=PolymorphicProxySerializer(
        component_name="AbstractCategoryPolymorphicSerializer",
        serializers=[CategorySerializer, SubCategorySerializer],
        resource_type_field_name=None,
    ),
)
class CategoryViewSet(OptionalPaginationMixin, viewsets.ReadOnlyModelViewSet):
    paginate_by_default = False
    serializer_class = AbstractCategoryPolymorphicSerializer
    queryset = AbstractCategory.objects.all().select_subclasses().select_related("subcategory__parent")\
                               .order_by("order").contains_fr_docs()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["parent_details"] = self.request.GET.get("parent_details", "true")
        return context


@extend_schema(
    description="Retrieve a top-down representation of categories, with each category containing zero or more sub-categories. "
                "Pagination is disabled by default.",
    parameters=OptionalPaginationMixin.PARAMETERS + PAGINATION_PARAMS,
)
class CategoryTreeViewSet(OptionalPaginationMixin, viewsets.ReadOnlyModelViewSet):
    paginate_by_default = False
    queryset = Category.objects.all().select_subclasses().prefetch_related(
        Prefetch("sub_categories", SubCategory.objects.all().order_by("order").contains_fr_docs()),
    ).order_by("order").contains_fr_docs()
    serializer_class = CategoryTreeSerializer
