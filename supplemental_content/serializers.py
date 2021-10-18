from rest_framework import serializers

from .models import (
    AbstractSupplementalContent,
    SupplementalContent,
    AbstractLocation,
    Section,
    Subpart,
    SubjectGroup,
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
        fields = "__all__"


class SubjectGroupSerializer(serializers.Serializer):
    subject_group_id = serializers.CharField()
    class Meta:
        model = SubjectGroup


class SectionSerializer(serializers.Serializer):
    section_id = serializers.IntegerField()
    class Meta:
        model = Subpart

# Serializers for children of Category

class CategorySerializer(PolymorphicSerializer):
    title = serializers.CharField()
    description = serializers.CharField()
    order = serializers.IntegerField()
    show_if_empty = serializers.BooleanField()

    def get_serializer_map(self):
        return {
            SubCategory: SubCategorySerializer,
            SubSubCategory: SubSubCategorySerializer,
        }

    class Meta:
        model = Category


class SubCategorySerializer(serializers.Serializer):
    parent = CategorySerializer()
    class Meta:
        model = SubCategory


class SubSubCategorySerializer(serializers.Serializer):
    parent = SubCategorySerializer()
    class Meta:
        model = SubSubCategory

# Serializers for children of AbstractSupplementalContent

class ApplicableSupplementalContentSerializer(serializers.ListSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return _make_category_tree(data)


class AbstractSupplementalContentSerializer(PolymorphicSerializer):
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    approved = serializers.BooleanField()
    category = CategorySerializer()
    locations = AbstractLocationSerializer(many=True)

    def get_serializer_map(self):
        return {
            SupplementalContent: SupplementalContentSerializer,
        }
    
    class Meta:
        model = AbstractSupplementalContent
        #list_serializer_class = ApplicableSupplementalContentSerializer


class SupplementalContentSerializer(serializers.Serializer):
    url = serializers.URLField()
    description = serializers.CharField()
    title = serializers.CharField()
    date = serializers.CharField()

    class Meta:
        model = SupplementalContent

# The following functions are related to generating a JSON structure for SupplementalContentView.
# This involves taking the 'parent = X' relationship of existing categories and reversing it so
# that each category instead has sub-categories and applicable supplemental content.


def _get_parents(category, memo):
    if category is None:
        return memo

    memo.append(category)
    return _get_parents(category.pop('parent', None), memo)


def _make_parent_tree(parents, tree):
    if len(parents) < 1:
        return

    parent = parents.pop()

    if parent['id'] not in tree.keys():
        tree[parent['id']] = parent
        tree[parent['id']]['sub_categories'] = {}
        tree[parent['id']]['supplemental_content'] = []

    if len(parents) < 1:
        return tree[parent['id']]

    return _make_parent_tree(parents, tree[parent['id']]['sub_categories'])


def _category_arrays(tree):
    t = tree.values()
    for category in t:
        category['sub_categories'] = _category_arrays(category['sub_categories'])
    return t


def _sort_categories(tree):
    tree = sorted(tree, key=lambda category: (category['order'], category['title']))
    for category in tree:
        category['sub_categories'] = _sort_categories(category['sub_categories'])
    return tree


def _make_category_tree(data):
    tree = {}
    for content in data:
        parents = _get_parents(content.pop('category'), [])
        parent = _make_parent_tree(parents, tree)
        parent['supplemental_content'].append(content)
    tree = _category_arrays(tree)
    return _sort_categories(tree)
