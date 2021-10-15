from rest_framework import serializers, generics
from django.db.models import Prefetch, Q

from .serializers import PolymorphicSerializer

from .models import (
    SupplementalContent,
    AbstractLocation,
    Section,
    Subpart,
    SubjectGroup,
)


# Serializers for children of AbstractLocation

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

# Serializers for children of Category

class CategorySerializer(serializers.Serializer):
    description = serializers.CharField()
    title = serializers.CharField()
    id = serializers.IntegerField()
    order = serializers.IntegerField()

    def get_fields(self):
        fields = super().get_fields()
        fields['parent'] = CategorySerializer()
        return fields

# Serializers for children of AbstractSupplementalContent

class ApplicableSupplementalContentSerializer(serializers.ListSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return _make_category_tree(data)


class SupplementalContentSerializer(serializers.Serializer):
    locations = AbstractLocationSerializer(many=True)
    category = CategorySerializer()
    url = serializers.URLField()
    description = serializers.CharField()
    title = serializers.CharField()
    date = serializers.CharField()

    class Meta:
        list_serializer_class = ApplicableSupplementalContentSerializer


class AbstractLocationView(generics.ListAPIView):
    serializer_class = AbstractLocationSerializer
    def get_queryset(self):
        query = AbstractLocation.objects.all()
        return query


class SupplementalContentView(generics.ListAPIView):
    serializer_class = SupplementalContentSerializer

    def get_queryset(self):
        title = self.kwargs.get("title")
        part = self.kwargs.get("part")
        section_list = self.request.GET.getlist("sections")
        subpart_list = self.request.GET.getlist("subparts")
        subjgrp_list = self.request.GET.getlist("subjectgroups")

        query = SupplementalContent.objects \
            .filter(
                Q(locations__section__section_id_in=section_list) |
                Q(locations__subpart__subpart_id_in=subpart_list) |
                Q(locations__subjectgroup__subject_group_id__in=subjgrp_list),
                approved=True,
                category__isnull=False,
                locations__title=title,
                locations__part=part,
            )\
            .prefetch_related(
                Prefetch(
                    'locations',
                    queryset=AbstractLocation.objects.filter(
                        Q(section__section_id_in=section_list) |
                        Q(subpart__subpart_id_in=subpart_list) |
                        Q(subjectgroup__subject_group_id__in=subjgrp_list),
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
