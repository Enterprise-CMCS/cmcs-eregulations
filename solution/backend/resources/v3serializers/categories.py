from rest_framework import serializers

from resources.models import Category, SubCategory
from .mixins import PolymorphicSerializer, OptionalFieldDetailsMixin


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

    def get_is_fr_doc_category(self, obj):
        try:
            return obj.is_fr_doc_category
        except Exception:
            return False


class SubCategorySerializer(OptionalFieldDetailsMixin, CategorySerializer):
    optional_details = {
        "parent": ("parent_details", "true", CategorySerializer, False),
    }


class CategoryTreeSerializer(CategorySerializer):
    sub_categories = CategorySerializer(many=True)
