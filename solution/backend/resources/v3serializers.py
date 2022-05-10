from rest_framework import serializers

from .models import (
    AbstractCategory,
    Category,
    SubCategory,
    Section,
    Subpart,
    FederalRegisterCategoryLink,
    AbstractResource,
    SupplementalContent,
    FederalRegisterDocument,
)


class PolymorphicSerializer(serializers.Serializer):
    def get_serializer_map(self):
        raise NotImplementedError

    def to_representation(self, instance):
        instance_type = type(instance)
        if instance_type in self.get_serializer_map():
            data = self.get_serializer_map()[instance_type][1](instance=instance, context=self.context).data
            data["type"] = self.get_serializer_map()[instance_type][0]
            return data


class AbstractCategoryPolymorphicSerializer(PolymorphicSerializer):
    def get_serializer_map(self):
        return {
            Category: ("category", CategorySerializer),
            SubCategory: ("subcategory", SubCategorySerializer),
        }


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    order = serializers.IntegerField()
    show_if_empty = serializers.BooleanField()


class SubCategorySerializer(CategorySerializer):
    parent = CategorySerializer()


class CategoryTreeSerializer(CategorySerializer):
    sub_categories = CategorySerializer(many=True)


class AbstractLocationPolymorphicSerializer(PolymorphicSerializer):
    def get_serializer_map(self):
        return {
            Section: ("section", SectionSerializer),
            Subpart: ("subpart", SubpartSerializer),
        }


class AbstractLocationSerializer(serializers.Serializer):
    title = serializers.IntegerField()
    part = serializers.IntegerField()


class SubpartSerializer(AbstractLocationSerializer):
    subpart_id = serializers.CharField()


class SectionSerializer(AbstractLocationSerializer):
    section_id = serializers.IntegerField()
    parent = serializers.PrimaryKeyRelatedField(read_only=True)


class AbstractResourcePolymorphicSerializer(PolymorphicSerializer):
    def get_serializer_map(self):
        return {
            SupplementalContent: ("supplemental_content", SupplementalContentSerializer),
            FederalRegisterDocument: ("federal_register_doc", FederalRegisterDocumentSerializer),
        }


class AbstractResourceSerializer(serializers.Serializer):
    created_at = serializers.CharField()
    updated_at = serializers.CharField()
    approved = serializers.BooleanField()

    def get_fields(self):
        fields = super(AbstractResourceSerializer, self).get_fields()
        fields["category"] = (
            AbstractCategoryPolymorphicSerializer()
            if self.context.get("category_details", "true").lower() == "true"
            else serializers.PrimaryKeyRelatedField(read_only=True)
        )
        fields["locations"] = (
            AbstractLocationPolymorphicSerializer(many=True)
            if self.context.get("location_details", "true").lower() == "true"
            else serializers.PrimaryKeyRelatedField(many=True, read_only=True)
        )
        return fields


class DateFieldSerializer(serializers.Serializer):
    date = serializers.CharField()


class TypicalResourceFieldsSerializer(DateFieldSerializer):
    name = serializers.CharField()
    description = serializers.CharField()
    url = serializers.CharField()
    
    name_headline = serializers.SerializerMethodField()
    description_headline = serializers.SerializerMethodField()


class SupplementalContentSerializer(AbstractResourceSerializer, TypicalResourceFieldsSerializer):
    def get_name_headline(self, obj):
        return getattr(obj, self.context["search_map"]["supplementalcontent__name_headline"], None)

    def get_description_headline(self, obj):
        return getattr(obj, self.context["search_map"]["supplementalcontent__description_headline"], None)


class FederalRegisterDocumentSerializer(AbstractResourceSerializer, TypicalResourceFieldsSerializer):
    docket_number = serializers.CharField()
    document_number = serializers.CharField()

    docket_number_headline = serializers.SerializerMethodField()
    document_number_headline = serializers.SerializerMethodField()

    def get_name_headline(self, obj):
        return getattr(obj, self.context["search_map"]["federalregisterdocument__name_headline"], None)

    def get_description_headline(self, obj):
        return getattr(obj, self.context["search_map"]["federalregisterdocument__description_headline"], None)

    def get_docket_number_headline(self, obj):
        return getattr(obj, self.context["search_map"]["federalregisterdocument__docket_number_headline"], None)

    def get_document_number_headline(self, obj):
        return getattr(obj, self.context["search_map"]["federalregisterdocument__document_number_headline"], None)


class FederalRegisterDocumentCreateSerializer(serializers.Serializer):
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
        try:
            category_link = FederalRegisterCategoryLink.objects.get(name=value)
        except FederalRegisterCategoryLink.DoesNotExist:
            try:
                category = AbstractCategory.objects.get(name=value)
            except AbstractCategory.DoesNotExist:
                category = Category.objects.create(name=value).abstractcategory_ptr
            category_link = FederalRegisterCategoryLink.objects.create(
                name=value,
                category=category,
            )
        return category_link.category.name

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
