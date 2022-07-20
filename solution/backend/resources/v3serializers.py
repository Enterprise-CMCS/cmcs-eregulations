from django.urls import reverse

from rest_framework import serializers

from .models import (
    AbstractCategory,
    Category,
    SubCategory,
    Section,
    Subpart,
    FederalRegisterCategoryLink,
    SupplementalContent,
    FederalRegisterDocument,
)


# Allows details of specified fields to be shown or hidden
# Must specify "optional_details" as map of strings to 4-tuples:
#    { "field_name": ("query_param", "default, true or false as a string", serializer class, many=True or False) }
class OptionalFieldDetailsMixin:
    def get_fields(self):
        fields = super().get_fields()
        for i in self.optional_details.items():
            fields[i[0]] = (
                i[1][2](many=i[1][3])
                if self.context.get(i[1][0], i[1][1]).lower() == "true"
                else serializers.PrimaryKeyRelatedField(many=i[1][3], read_only=True)
            )
        return fields


# Retrieves automatically generated search headlines
class HeadlineField(serializers.Field):
    def __init__(self, model_name, **kwargs):
        self.model_name = model_name
        kwargs["source"] = '*'
        kwargs["read_only"] = True
        super().__init__(**kwargs)

    def to_representation(self, obj):
        return getattr(obj, f"{self.model_name}_{self.field_name}", getattr(obj, self.field_name, None))


# Allows subclasses to be serialized independently
# Must implement get_serializer_map as map of classes to 2-tuples:
#    { model_class: ("model_name", serializer_class) }
class PolymorphicSerializer(serializers.Serializer):
    def get_serializer_map(self):
        raise NotImplementedError

    def to_representation(self, instance):
        instance_type = type(instance)
        if instance_type in self.get_serializer_map():
            data = self.get_serializer_map()[instance_type][1](instance=instance, context=self.context).data
            data["type"] = self.get_serializer_map()[instance_type][0]
            return data
        return "Serializer not available"


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


class SubCategorySerializer(OptionalFieldDetailsMixin, CategorySerializer):
    optional_details = {
        "parent": ("parent_details", "true", CategorySerializer, False),
    }


class CategoryTreeSerializer(CategorySerializer):
    sub_categories = CategorySerializer(many=True)


class AbstractLocationPolymorphicSerializer(PolymorphicSerializer):
    def get_serializer_map(self):
        return {
            Section: ("section", SectionSerializer),
            Subpart: ("subpart", SubpartSerializer),
        }


class AbstractLocationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.IntegerField()
    part = serializers.IntegerField()


class SubpartSerializer(AbstractLocationSerializer):
    subpart_id = serializers.CharField()


class SectionSerializer(AbstractLocationSerializer):
    section_id = serializers.IntegerField()
    parent = serializers.PrimaryKeyRelatedField(read_only=True)


class FullSectionSerializer(SectionSerializer):
    parent = AbstractLocationPolymorphicSerializer()


class FullSubpartSerializer(SubpartSerializer):
    children = AbstractLocationPolymorphicSerializer(many=True)


class AbstractResourcePolymorphicSerializer(PolymorphicSerializer):
    def get_serializer_map(self):
        return {
            SupplementalContent: ("supplemental_content", SupplementalContentSerializer),
            FederalRegisterDocument: ("federal_register_doc", FederalRegisterDocumentSerializer),
        }


class AbstractResourceSerializer(OptionalFieldDetailsMixin, serializers.Serializer):
    id = serializers.IntegerField()
    created_at = serializers.CharField()
    updated_at = serializers.CharField()
    approved = serializers.BooleanField()

    optional_details = {
        "category": ("category_details", "true", AbstractCategoryPolymorphicSerializer, False),
        "locations": ("location_details", "true", AbstractLocationPolymorphicSerializer, True),
    }


class DateFieldSerializer(serializers.Serializer):
    date = serializers.CharField()


# Provides fields most often used in resources
class TypicalResourceFieldsSerializer(DateFieldSerializer):
    name = serializers.CharField()
    description = serializers.CharField()
    url = serializers.CharField()
    internalURL = serializers.SerializerMethodField()

    def get_internalURL(self, obj):
        return reverse('supplemental_content', kwargs={'id': obj.pk})


class SupplementalContentSerializer(AbstractResourceSerializer, TypicalResourceFieldsSerializer):
    name_headline = HeadlineField("supplementalcontent")
    description_headline = HeadlineField("supplementalcontent")


class FederalRegisterDocumentSerializer(AbstractResourceSerializer, TypicalResourceFieldsSerializer):
    docket_number = serializers.CharField()
    document_number = serializers.CharField()

    name_headline = HeadlineField("federalregisterdocument")
    description_headline = HeadlineField("federalregisterdocument")
    docket_number_headline = HeadlineField("federalregisterdocument")
    document_number_headline = HeadlineField("federalregisterdocument")


class SectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = "__all__"


class FederalRegisterDocumentCreateSerializer(serializers.Serializer):
    category = serializers.CharField()
    locations = SectionCreateSerializer(many=True, allow_null=True)
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
            location.save()
            locations.append(location)
        instance.locations.set(locations)

        # save and return
        instance.save()
        return instance
