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
            PublicCategory: ("public_category", PublicCategoryIDSerializer),
            PublicSubCategory: ("public_subcategory", PublicSubCategoryIDSerializer),
            InternalCategory: ("internal_category", InternalCategoryIDSerializer),
            InternalSubCategory: ("internal_subcategory", InternalSubCategoryIDSerializer),
        }


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    order = serializers.IntegerField()
    show_if_empty = serializers.BooleanField()
    type = PolymorphicTypeField()


class PublicSubCategoryIDSerializer(CategorySerializer):
    parent = serializers.PrimaryKeyRelatedField(read_only=True)


class PublicCategoryIDSerializer(CategorySerializer):
    subcategories = serializers.PrimaryKeyRelatedField(read_only=True, many=True)


class InternalSubCategoryIDSerializer(CategorySerializer):
    parent = serializers.PrimaryKeyRelatedField(read_only=True)


class InternalCategoryIDSerializer(CategorySerializer):
    subcategories = serializers.PrimaryKeyRelatedField(read_only=True, many=True)


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
