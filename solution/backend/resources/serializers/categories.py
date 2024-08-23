from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from resources.models import (
    InternalCategory,
    InternalSubCategory,
    PublicCategory,
    PublicSubCategory,
)

from .polymorphic import (
    PolymorphicSerializer,
    PolymorphicTypeField,
    ProxySerializerWrapper,
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
    @extend_schema_field(serializers.IntegerField())
    def get_parent(self, obj):
        return obj.parent.id if obj.parent else None

    parent = serializers.SerializerMethodField()


class PublicCategoryWithSubCategoriesSerializer(CategorySerializer):
    subcategories = PublicSubCategorySerializer(many=True)


class PublicCategorySerializer(CategorySerializer):
    pass


class InternalSubCategorySerializer(CategorySerializer):
    @extend_schema_field(serializers.IntegerField())
    def get_parent(self, obj):
        return obj.parent.id if obj.parent else None

    parent = serializers.SerializerMethodField()


class InternalCategoryWithSubCategoriesSerializer(CategorySerializer):
    subcategories = InternalSubCategorySerializer(many=True)


class InternalCategorySerializer(CategorySerializer):
    pass


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
