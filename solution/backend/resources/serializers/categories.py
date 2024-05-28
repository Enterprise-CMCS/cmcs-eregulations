from drf_spectacular.utils import OpenApiTypes, extend_schema_field
from rest_framework import serializers

from .polymorphic import (
    PolymorphicSerializer,
    PolymorphicTypeField,
    ProxySerializerWrapper,
)

from resources.models import (
    NewAbstractCategory,
    AbstractPublicCategory,
    PublicCategory,
    PublicSubCategory,
    AbstractInternalCategory,
    InternalCategory,
    InternalSubCategory,
)


class AbstractCategorySerializer(PolymorphicSerializer):
    def get_serializer_map(self):
        return {
            PublicCategory: ("public_category", PublicCategorySerializer),
            PublicSubCategory: ("public_subcategory", PublicSubCategorySerializer),
            InternalCategory: ("internal_category", InternalCategorySerializer),
            InternalSubCategory: ("internal_subcategory", InternalSubCategorySerializer),
        }


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    order = serializers.IntegerField()
    show_if_empty = serializers.BooleanField()
    is_fr_link_category = serializers.BooleanField()
    type = PolymorphicTypeField()


class PublicSubCategorySerializer(CategorySerializer):
    pass


class PublicCategorySerializer(CategorySerializer):
    subcategories = PublicSubCategorySerializer(many=True)


class InternalSubCategorySerializer(CategorySerializer):
    pass


class InternalCategorySerializer(CategorySerializer):
    subcategories = InternalSubCategorySerializer(many=True)


MetaCategorySerializer = ProxySerializerWrapper(
    component_name="MetaCategorySerializer",
    resource_type_field_name="type",
    serializers=[
        PublicCategorySerializer,
        PublicSubCategorySerializer,
        InternalCategorySerializer,
        InternalSubCategorySerializer,
    ],
)
