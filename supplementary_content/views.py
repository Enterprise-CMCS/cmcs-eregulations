from rest_framework import serializers, generics
from rest_framework.response import Response
from django.db.models import Prefetch, Count, Q


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

    def get_queryset(self):
        section_list = self.request.GET.getlist("sections")
        title = self.kwargs.get("title")
        part = self.kwargs.get("part")
        query = Category.objects.prefetch_related(
            Prefetch(
                'supplementary_content',
                queryset=SupplementaryContent.objects.filter(approved=True).prefetch_related(
                    Prefetch(
                        'sections',
                        queryset=RegulationSection.objects.filter(
                            title=title,
                            part=part,
                            section__in=section_list,
                        )
                    )
                ).distinct(),
            )
        ).annotate(
            content_count=Count(
                'supplementary_content',
                distinct=True,
                filter=Q(
                    supplementary_content__approved=True,
                    supplementary_content__sections__title=title,
                    supplementary_content__sections__part=part,
                    supplementary_content__sections__section__in=section_list,
                )
            )
        ).filter(content_count__gt=0)
        return query

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(_make_category_tree(serializer.data))


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
