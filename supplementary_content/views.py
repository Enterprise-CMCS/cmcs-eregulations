from rest_framework import serializers, generics
from rest_framework.response import Response


from .models import (
    Category,
    SupplementaryContent,
    RegulationSection,
)


class RegulationSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegulationSection
        fields = ("title", "part", "subpart", "section")


class SupplementaryContentSerializer(serializers.ModelSerializer):
    sections = RegulationSectionSerializer(many=True)

    class Meta:
        model = SupplementaryContent
        fields = ("url", "title", "description", "date", "created_at", "updated_at", "category", "sections")


class CategorySerializer(serializers.ModelSerializer):
    supplementary_content = SupplementaryContentSerializer(many=True)

    class Meta:
        model = Category
        fields = ("id", "parent", "title", "description", "supplementary_content")

    def get_fields(self):
        fields = super(CategorySerializer, self).get_fields()
        fields['parent'] = CategorySerializer()
        return fields


class SupplementaryContentView(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        section_list = self.request.GET.getlist("sections")
        title = self.kwargs.get("title")
        part = self.kwargs.get("part")
        query = Category.objects.filter(
            supplementary_content__sections__title=title,
            supplementary_content__sections__part=part,
            supplementary_content__sections__section__in=section_list,
        ).distinct()
        return query

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(_make_category_tree(serializer.data))


def _add_category(category):
    return {
        'id': category['id'],
        'title': category['title'],
        'description': category['description'],
        'supplementary_content': category.get('supplementary_content', []),
        'sub_categories': [],
    }


def _make_category_stack(category):
    stack = [category]
    current = category
    while current['parent'] is not None:
        stack.append(current['parent'])
        current = current['parent']
    return stack


def _get_category(tree, id):
    for category in tree:
        if category['id'] == id:
            return category
    return None


def _make_category_tree(data):
    tree = []
    for category in data:
        stack = _make_category_stack(category)
        node = tree
        while len(stack) > 0:
            current = stack.pop()
            sub_node = _get_category(node, current['id'])
            if sub_node == None:
                sub_node = _add_category(current)
                node.append(sub_node)
            node = sub_node['sub_categories']
    return tree
