from django.db.models.fields import IntegerField
from rest_framework import serializers

from .models import (
    AbstractSupplementalContent,
    SupplementalContent,
    AbstractLocation,
    Section,
    Subpart,
    SubjectGroup,
    AbstractCategory,
    Category,
    SubCategory,
    SubSubCategory,
)


class PolymorphicSerializer(serializers.Serializer):
    def get_serializer_map(self):
        raise NotImplementedError()

    def to_representation(self, obj):
        data = super().to_representation(obj)
        data["object_type"] = self.Meta.model.__name__.lower()
        for subclass in self.Meta.model.__subclasses__():
            name = subclass.__name__.lower()
            child = getattr(obj, name, None)
            if child:
                data["object_type"] = name
                serializer = self.get_serializer_map().get(subclass, None)
                if serializer:
                    return {**data, **(serializer(child, context=self.context).to_representation(child))}
        return data

# Serializers for children of AbstractLocation

class AbstractLocationSerializer(PolymorphicSerializer):
    title = serializers.IntegerField()
    part = serializers.IntegerField()

    def get_serializer_map(self):
        return {
            Subpart: SubpartSerializer,
            SubjectGroup: SubjectGroupSerializer,
            Section: SectionSerializer,
        }

    class Meta:
        model = AbstractLocation


class SubpartSerializer(serializers.Serializer):
    subpart_id = serializers.CharField()
    class Meta:
        model = Subpart


class SubjectGroupSerializer(serializers.Serializer):
    subject_group_id = serializers.CharField()
    class Meta:
        model = SubjectGroup


class SectionSerializer(serializers.Serializer):
    section_id = serializers.IntegerField()
    class Meta:
        model = Subpart

# Serializers for children of Category

class AbstractCategorySerializer(PolymorphicSerializer):
    title = serializers.CharField()
    description = serializers.CharField()
    order = serializers.IntegerField()
    show_if_empty = serializers.BooleanField()
    id = serializers.IntegerField()

    def get_serializer_map(self):
        return {
            Category: CategorySerializer,
            SubCategory: SubCategorySerializer,
            SubSubCategory: SubSubCategorySerializer,
        }

    class Meta:
        model = AbstractCategory


class CategorySerializer(serializers.Serializer):
    class Meta:
        model = Category


class SubCategorySerializer(serializers.Serializer):
    parent = AbstractCategorySerializer()
    class Meta:
        model = SubCategory


class SubSubCategorySerializer(serializers.Serializer):
    parent = AbstractCategorySerializer()
    class Meta:
        model = SubSubCategory

# Serializers for children of AbstractSupplementalContent

class ApplicableSupplementalContentSerializer(serializers.ListSerializer):
    def to_representation(self, instance):
        supplemental_content = super().to_representation(instance)
        categories = self._get_categories(supplemental_content)
        tree, flat_tree = self._make_category_trees(categories)
        self._add_supplemental_content(flat_tree, supplemental_content)
        return self._to_array(tree)
    
    def _add_supplemental_content(self, flat_tree, supplemental_content):
        for content in supplemental_content:
            category = flat_tree[content["category"]["id"]]
            category["supplemental_content"].append(content)
    
    def _get_categories(self, supplemental_content):
        raw_categories = AbstractCategory.objects.filter(show_if_empty=True).distinct()
        categories = AbstractCategorySerializer(raw_categories, many=True).to_representation(raw_categories)
        for content in supplemental_content:
            categories.append(content["category"])
        return categories
    
    def _make_category_trees(self, categories):
        tree = {}
        flat_tree = {}
        for category in categories:
            stack = [category]
            while "parent" in category:
                category = category["parent"]
                stack.append(category)
            self._unwind_stack(tree, flat_tree, stack)
        return tree, flat_tree

    def _unwind_stack(self, tree, flat_tree, stack):
        if len(stack) < 1:
            return
        node = stack.pop()
        if node["id"] not in tree:
            tree[node["id"]] = {
                "title": node["title"],
                "description": node["description"],
                "order": node["order"],
                "show_if_empty": node["show_if_empty"],
                "sub_categories": {},
                "supplemental_content": [],
            }
            flat_tree[node["id"]] = tree[node["id"]]
        self._unwind_stack(tree[node["id"]]["sub_categories"], flat_tree, stack)
    
    def _to_array(self, tree):
        t = tree.values()
        for category in t:
            category["sub_categories"] = self._to_array(category["sub_categories"])
        return t


class AbstractSupplementalContentSerializer(PolymorphicSerializer):
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    approved = serializers.BooleanField()
    category = AbstractCategorySerializer()
    locations = AbstractLocationSerializer(many=True)

    def get_serializer_map(self):
        return {
            SupplementalContent: SupplementalContentSerializer,
        }
    
    class Meta:
        model = AbstractSupplementalContent
        list_serializer_class = ApplicableSupplementalContentSerializer


class SupplementalContentSerializer(serializers.Serializer):
    url = serializers.URLField()
    description = serializers.CharField()
    title = serializers.CharField()
    date = serializers.CharField()

    class Meta:
        model = SupplementalContent
