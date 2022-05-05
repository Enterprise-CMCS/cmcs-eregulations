from rest_framework import serializers

from .models import (
    AbstractCategory,
    Category,
    Section,
    FederalRegisterCategoryLink,
)


class SectionSerializer(serializers.Serializer):
    title = serializers.IntegerField()
    part = serializers.IntegerField()
    section_id = serializers.IntegerField()


class FRDocCreateSerializer(serializers.Serializer):
    category = serializers.CharField()
    locations = SectionSerializer(many=True, allow_null=True)
    url = serializers.URLField(allow_blank=True, allow_null=True)
    description = serializers.CharField(allow_blank=True, allow_null=True)
    name = serializers.CharField(allow_blank=True, allow_null=True)
    docket_number = serializers.CharField(allow_blank=True, allow_null=True)
    document_number = serializers.CharField(allow_blank=True, allow_null=True)
    date = serializers.CharField(allow_blank=True, allow_null=True)
    approved = serializers.BooleanField(required=False, default=False)
    id = serializers.CharField(required=False)

    def validate_category(self, value):
        category_name = Category_Map.get(value, value)
        try:
            AbstractCategory.objects.get(name=category_name)
        except AbstractCategory.DoesNotExist:
            # Just make one that makes sense
            # can't use get_or_create because it is not abstract
            Category.objects.create(name=category_name)
        return category_name

    def update(self, instance, validated_data):
        # set basic fields
        instance.url = validated_data.get('url', instance.url)
        instance.description = validated_data.get('description', instance.description)
        instance.name = validated_data.get('name', instance.name)
        instance.docket_number = validated_data.get('docket_number', instance.docket_number)
        instance.document_number = validated_data.get('document_number', instance.document_number)
        instance.date = validated_data.get('date', instance.date)
        instance.approved = validated_data.get('approved', instance.approved)
        # This will work because it was validated above
        category = AbstractCategory.objects.get(name=validated_data["category"])
        instance.category = category

        # set the locations on the instance
        locations = []
        for loc in (validated_data["locations"] or []):
            title = loc["title"]
            part = loc["part"]
            section_id = loc["section_id"]
            location, _ = Section.objects.get_or_create(title=title, part=part, section_id=section_id)
            location.display_name = location.__str__()
            location.save()
            locations.append(location)
        instance.locations.set(locations)

        # save and return
        instance.save()
        return instance
