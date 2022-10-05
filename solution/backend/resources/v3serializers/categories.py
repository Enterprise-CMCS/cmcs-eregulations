from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field, OpenApiTypes, PolymorphicProxySerializer

from resources.models import Category, SubCategory
from .mixins import PolymorphicSerializer
from .utils import ProxySerializerWrapper


class AbstractCategoryPolymorphicSerializer(PolymorphicSerializer):
    def get_serializer_map(self):
        return {
            Category: ("category", CategorySerializer),
            SubCategory: ("subcategory", SubCategorySerializer),
        }


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    order = serializers.IntegerField()
    show_if_empty = serializers.BooleanField()
    is_fr_doc_category = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_fr_doc_category(self, obj):
        try:
            return obj.is_fr_doc_category
        except Exception:
            return False


class SubCategorySerializer(CategorySerializer):
    parent = serializers.SerializerMethodField()

    @extend_schema_field(CategorySerializer)
    def get_parent(self, obj):
        if self.context.get("parent_details", "true").lower() == "true":
            return CategorySerializer(obj.category).data
        return serializers.PrimaryKeyRelatedField(read_only=True)


MetaCategorySerializer = ProxySerializerWrapper(
    component_name="MetaCategorySerializer",
    serializers=[CategorySerializer, SubCategorySerializer],
    resource_type_field_name="type",
)


class CategoryTreeSerializer(CategorySerializer):
    sub_categories = CategorySerializer(many=True)
