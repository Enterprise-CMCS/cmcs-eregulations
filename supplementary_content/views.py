import supplementary_content
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
        fields = ("title", "part", "subpart", "section", "supplementary_content")


class SupplementaryContentSerializer(serializers.ModelSerializer):
    sections = RegulationSectionSerializer(many=True)
    class Meta:
        model = SupplementaryContent
        fields = ("url", "title", "description", "date", "created_at", "updated_at", "category", "sections")


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("parent", "title", "description",)

    def get_fields(self):
        fields = super(ParentSerializer, self).get_fields()
        fields['parent'] = ParentSerializer()
        return fields


class CategorySerializer(serializers.ModelSerializer):
    supplementary_content = SupplementaryContentSerializer(many=True)
    parent = ParentSerializer()

    class Meta:
        model = Category
        fields = ("parent", "title", "description", "supplementary_content")


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

        categories = Category.objects.all()
        return Response(serializer.data)

