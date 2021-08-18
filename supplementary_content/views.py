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


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "parent", "title", "description",)

    def get_fields(self):
        fields = super(ParentSerializer, self).get_fields()
        fields['parent'] = ParentSerializer()
        return fields


class CategorySerializer(serializers.ModelSerializer):
    supplementary_content = SupplementaryContentSerializer(many=True)
    parent = ParentSerializer()

    class Meta:
        model = Category
        fields = ("id", "parent", "title", "description", "supplementary_content")


class SupplementaryContentView(generics.ListAPIView):
    serializer_class = CategorySerializer

    section_list = []
    title = None
    part = None

    def get_queryset(self):
        self.section_list = self.request.GET.getlist("sections")
        self.title = self.kwargs.get("title")
        self.part = self.kwargs.get("part")
        query = Category.objects.filter(
            supplementary_content__sections__title=self.title,
            supplementary_content__sections__part=self.part,
            supplementary_content__sections__section__in=self.section_list,
        ).distinct()
        return query

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        category_tree = _make_category_tree(serializer.data)
        _filter_content(category_tree, self.title, self.part, self.section_list)
        return Response(category_tree)


# The following functions are related to generating a JSON structure for SupplementaryContentView.
# This involves taking the 'parent = X' relationship of existing categories and reversing it so
# that each category instead has sub-categories. We also include a function for filtering out
# supplementary content from the resulting tree that does not match the requested sections.


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


def _matches_sections(content, title, part, sections):
    for section in content['sections']:
        if section['section'] in sections and section['title'] == title and section['part'] == part:
            return True
    return False


def _filter_content(tree, title, part, sections):
    for category in tree:
        new_content = [item for item in category['supplementary_content'] if _matches_sections(item, title, part, sections)]
        category['supplementary_content'] = new_content
        _filter_content(category['sub_categories'], title, part, sections)


def _make_category_tree(data):
    tree = []
    for category in data:
        stack = _make_category_stack(category)
        node = tree
        while len(stack) > 0:
            current = stack.pop()
            sub_node = _get_category(node, current['id'])
            if sub_node is None:
                sub_node = _add_category(current)
                node.append(sub_node)
            elif 'supplementary_content' in current:
                sub_node['supplementary_content'] = current['supplementary_content']
            node = sub_node['sub_categories']
    return tree
