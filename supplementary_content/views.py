from rest_framework import serializers, generics

from .models import (
    Category,
    SupplementaryContent,
    RegulationSection,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("parent", "title", "description")


class RegulationSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegulationSection
        fields = ("title", "part", "subpart", "section", "supplementary_content")


class SupplementaryContentSerializer(serializers.ModelSerializer):
    sections = RegulationSectionSerializer(many=True)
    class Meta:
        model = SupplementaryContent
        fields = ("url", "title", "description", "date", "created_at", "updated_at", "category", "sections")


class SupplementaryContentView(generics.ListAPIView):
    serializer_class = SupplementaryContentSerializer

    def get_queryset(self):
        section_list = self.request.GET.getlist("sections")
        title = self.kwargs.get("title")
        part = self.kwargs.get("part")
        query = SupplementaryContent.objects.filter(sections__title=title, sections__part=part, sections__section__in=section_list).distinct()
        return query
