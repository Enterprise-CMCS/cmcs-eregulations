from rest_framework import serializers, generics
from django.db.models import Prefetch


from .models import (
    SupplementalContent,
    RegulationSection,
)


class RegulationSectionSerializer(serializers.Serializer):
    title = serializers.IntegerField()
    part = serializers.IntegerField()
    section = serializers.IntegerField()


class CategorySerializer(serializers.Serializer):
    description = serializers.CharField()
    title = serializers.CharField()
    id = serializers.IntegerField()
    order = serializers.IntegerField()

    def get_fields(self):
        fields = super().get_fields()
        fields['parent'] = CategorySerializer()
        return fields


class ApplicableSupplementalContentSerializer(serializers.ListSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return _make_category_tree(data)


class SupplementalContentSerializer(serializers.Serializer):
    sections = RegulationSectionSerializer(many=True)
    category = CategorySerializer()
    url = serializers.URLField()
    description = serializers.CharField()
    title = serializers.CharField()
    date = serializers.CharField()

    class Meta:
        list_serializer_class = ApplicableSupplementalContentSerializer


class SupplementalContentView(generics.ListAPIView):
    serializer_class = SupplementalContentSerializer

    def get_queryset(self):
        section_list = self.request.GET.getlist("sections")
        title = self.kwargs.get("title")
        part = self.kwargs.get("part")
        query = SupplementalContent.objects \
            .filter(
                approved=True,
                category__isnull=False,
                sections__title=title,
                sections__part=part,
                sections__section__in=section_list,
            )\
            .prefetch_related(
                Prefetch(
                    'sections',
                    queryset=RegulationSection.objects.filter(
                        title=title,
                        part=part,
                        section__in=section_list,
                    )
                )
            ).distinct().order_by('-date', 'title')
        return query


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
