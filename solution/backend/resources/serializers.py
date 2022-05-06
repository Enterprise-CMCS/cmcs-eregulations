from rest_framework import serializers

from .utils import reverse_sort

from .models import (
    AbstractSupplementalContent,
    SupplementalContent,
    AbstractLocation,
    Section,
    Subpart,
    AbstractCategory,
    Category,
    SubCategory,
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
            Section: SectionSerializer,
        }

    class Meta:
        model = AbstractLocation


class SimpleLocationSerializer(serializers.Serializer):
    title = serializers.IntegerField()
    part = serializers.IntegerField()
    display_name = serializers.CharField()

    class Meta:
        model = AbstractLocation


class SubpartSerializer(serializers.Serializer):
    subpart_id = serializers.CharField()

    class Meta:
        model = Subpart


class SectionSerializer(AbstractLocationSerializer):
    section_id = serializers.IntegerField()

    class Meta:
        model = Subpart


# Serializers for children of Category


class AbstractCategorySerializer(PolymorphicSerializer):
    name = serializers.CharField()
    description = serializers.CharField()
    order = serializers.IntegerField()
    show_if_empty = serializers.BooleanField()
    id = serializers.IntegerField()

    def get_serializer_map(self):
        return {
            Category: CategorySerializer,
            SubCategory: SubCategorySerializer,
        }

    class Meta:
        model = AbstractCategory


class SimpleCategorySerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    order = serializers.IntegerField()
    show_if_empty = serializers.BooleanField()
    id = serializers.IntegerField()
    display_name = serializers.CharField()

    class Meta:
        model = AbstractCategory


class CategorySerializer(serializers.Serializer):
    class Meta:
        model = Category


class SubCategorySerializer(serializers.Serializer):
    parent = AbstractCategorySerializer()

    class Meta:
        model = SubCategory


# Serializers for children of AbstractSupplementalContent


class ApplicableSupplementalContentSerializer(serializers.ListSerializer):
    def to_representation(self, instance):
        supplemental_content = super().to_representation(instance)
        categories = self._get_categories()
        tree, flat_tree = self._make_category_trees(categories)
        self._add_supplemental_content(flat_tree, supplemental_content)
        return self._sort(self._to_array(tree))

    def _add_supplemental_content(self, flat_tree, supplemental_content):
        for content in supplemental_content:
            category = flat_tree[content["category"]["id"]]
            del content["category"]
            category["supplemental_content"].append(content)

    def _get_categories(self):
        raw_categories = AbstractCategory.objects.all().select_subclasses()
        categories = AbstractCategorySerializer(raw_categories, many=True).to_representation(raw_categories)
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
                "name": node["name"],
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

    def _sort(self, tree):
        tree = sorted(tree, key=lambda category: (category["order"], category["name"]))
        result = []
        for category in tree:
            category["supplemental_content"] = sorted(
                category["supplemental_content"],
                key=lambda content: (
                    reverse_sort(content["date"] or ""),
                    content["name"] or "",
                ),
            )
            category["sub_categories"] = self._sort(category["sub_categories"])
            # only keep populated categories
            if len(category["supplemental_content"]) or len(category["sub_categories"]) or category["show_if_empty"]:
                result.append(category)
        return result


class AbstractSupplementalContentSerializer(PolymorphicSerializer):
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    approved = serializers.BooleanField()
    category = SimpleCategorySerializer()
    locations = SimpleLocationSerializer(many=True)
    id = serializers.CharField()

    def get_serializer_map(self):
        return {
            SupplementalContent: SupplementalContentSerializer,
        }

    class Meta:
        model = AbstractSupplementalContent
        list_serializer_class = ApplicableSupplementalContentSerializer


class SupIDSerializer(serializers.Serializer):
    id = serializers.CharField()

    class Meta:
        model = AbstractSupplementalContent


class SupplementalContentSerializer(serializers.Serializer):
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    approved = serializers.BooleanField()
    category = SimpleCategorySerializer()
    locations = SimpleLocationSerializer(many=True)
    url = serializers.URLField()
    description = serializers.CharField()
    name = serializers.CharField()
    date = serializers.CharField()
    nameHeadline = serializers.CharField(required=False)
    descriptionHeadline = serializers.CharField(required=False)

    class Meta:
        model = SupplementalContent
        list_serializer_class = ApplicableSupplementalContentSerializer


class FlatSupplementalContentSerializer(serializers.Serializer):
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    approved = serializers.BooleanField()
    category = SimpleCategorySerializer()
    locations = SimpleLocationSerializer(many=True)
    url = serializers.URLField()
    description = serializers.CharField()
    name = serializers.CharField()
    date = serializers.CharField()
    nameHeadline = serializers.SerializerMethodField()
    descriptionHeadline = serializers.SerializerMethodField()

    class Meta:
        model = AbstractSupplementalContent

    def get_nameHeadline(self, obj):
        try:
            return obj.nameHeadline
        except Exception:
            return None

    def get_descriptionHeadline(self, obj):
        try:
            return obj.descriptionHeadline
        except Exception:
            return None


class IndividualSupSerializer(PolymorphicSerializer):
    id = serializers.CharField()

    locations = SimpleLocationSerializer(many=True)

    def get_serializer_map(self):
        return {
            SupplementalContent: SupplementalContentSerializer,
        }

    class Meta:
        model = AbstractSupplementalContent


class SuppByLocationSerializer(serializers.ModelSerializer):
    supplemental_content = SupIDSerializer(many=True)

    def get_serializer_map(self):
        return {
            SupplementalContent: SupIDSerializer,
        }

    class Meta:
        model = AbstractLocation
        fields = "__all__"
