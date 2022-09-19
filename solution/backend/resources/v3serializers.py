
from django.urls import reverse

from rest_framework import serializers

from .models import (
    AbstractCategory,
    Category,
    SubCategory,
    Section,
    Subpart,
    SupplementalContent,
    FederalRegisterDocument,
    FederalRegisterDocumentGroup,
    ResourcesConfiguration,
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
    is_fr_doc_category = serializers.SerializerMethodField()

    def get_is_fr_doc_category(self, obj):
        try:
            return obj.is_fr_doc_category
        except Exception:
            return False


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


class SimpleFederalRegisterDocumentSerializer(AbstractResourceSerializer, TypicalResourceFieldsSerializer):
    docket_numbers = serializers.ListField(child=serializers.CharField())
    document_number = serializers.CharField()
    doc_type = serializers.CharField()

    name_headline = HeadlineField("federalregisterdocument")
    description_headline = HeadlineField("federalregisterdocument")
    document_number_headline = HeadlineField("federalregisterdocument")


class FederalRegisterDocumentSerializer(SimpleFederalRegisterDocumentSerializer):
    related_docs = SimpleFederalRegisterDocumentSerializer(many=True, source="related_resources")

    def to_representation(self, instance):
        obj = super().to_representation(instance)
        if self.context['fr_grouping'] == 'false':
            return obj
        docs = [obj] + obj["related_docs"]
        del obj["related_docs"]
        docs = sorted(docs, key=lambda i: i["date"] or "", reverse=True)
        docs[0]["related_docs"] = docs[1:]
        return docs[0]


class SectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = "__all__"


class SectionRangeCreateSerializer(serializers.Serializer):
    title = serializers.CharField()
    part = serializers.CharField()
    first_sec = serializers.IntegerField()
    last_sec = serializers.IntegerField()


class FederalRegisterDocumentCreateSerializer(serializers.Serializer):
    sections = SectionCreateSerializer(many=True, allow_null=True)
    section_ranges = SectionRangeCreateSerializer(many=True, allow_null=True, required=False)
    url = serializers.URLField(allow_blank=True, allow_null=True)
    description = serializers.CharField(allow_blank=True, allow_null=True)
    name = serializers.CharField(allow_blank=True, allow_null=True)
    docket_numbers = serializers.ListField(child=serializers.CharField())
    document_number = serializers.CharField(allow_blank=True, allow_null=True)
    date = serializers.CharField(allow_blank=True, allow_null=True)
    approved = serializers.BooleanField(required=False, default=False)
    id = serializers.CharField(required=False)
    doc_type = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    def get_category(self):
        config = ResourcesConfiguration.objects.first()
        category = config.fr_doc_category
        if not category:
            try:
                category = AbstractCategory.objects.get(name="Federal Register Docs")
            except AbstractCategory.DoesNotExist:
                category = Category.objects.create(name="Federal Register Docs")
            config.fr_doc_category = category
            config.save()
        return category

    def validate_doc_type(self, value):
        if value == "Rule" or value == "Final Rules":
            return "Final"
        if value == "Proposed Rules" or value == "Proposed Rule":
            return "NPRM"
        return value

    def update(self, instance, validated_data):
        # set basic fields
        instance.url = validated_data.get('url', instance.url)
        instance.description = validated_data.get('description', instance.description)
        instance.name = validated_data.get('name', instance.name)
        instance.docket_numbers = validated_data.get('docket_numbers', instance.docket_numbers)
        instance.document_number = validated_data.get('document_number', instance.document_number)
        instance.date = validated_data.get('date', instance.date)
        instance.approved = validated_data.get('approved', instance.approved)
        instance.doc_type = validated_data.get('doc_type', instance.doc_type)
        instance.category = self.get_category()

        # set the locations on the instance
        locations = []
        for loc in (validated_data["sections"] or []):
            title = loc["title"]
            part = loc["part"]
            section_id = loc["section_id"]
            location, _ = Section.objects.get_or_create(title=title, part=part, section_id=section_id)
            location.save()
            locations.append(location)

        for loc_range in (validated_data["section_ranges"] or []):
            title = loc_range['title']
            part = loc_range['part']
            first_section = loc_range['first_sec']
            last_section = loc_range['last_sec']
            Section.objects.get_or_create(title=title, part=part, section_id=first_section)
            Section.objects.get_or_create(title=title, part=part, section_id=last_section)
            sections = Section.objects.filter(title=title, part=part, section_id__range=(first_section, last_section))
            locations.extend(list(sections))
        instance.locations.set(locations)

        # set the group on the instance
        prefixes = []
        for i in instance.docket_numbers:
            d = i.split("-")
            if len(d) > 1:
                prefixes.append("-".join(d[0:-1]) + "-")
        if len(prefixes) > 0:
            groups = FederalRegisterDocumentGroup.objects.filter(docket_number_prefixes__overlap=prefixes)
            if len(groups) == 0:
                group = FederalRegisterDocumentGroup.objects.create(docket_number_prefixes=prefixes)
            else:
                group = self.combine_groups(groups) if len(groups) > 1 else groups[0]
            group.docket_number_prefixes = list(set(group.docket_number_prefixes + prefixes))
            group.save()
            instance.group = group

        # save and return
        instance.save()
        return instance

    def combine_groups(self, groups):
        main = groups[0]
        docs = main.documents.all()
        prefixes = main.docket_number_prefixes
        for group in groups[1:]:
            docs |= group.documents.all()
            prefixes += group.docket_number_prefixes
            group.delete()
        main.documents.set(docs.distinct())
        main.docket_number_prefixes = list(set(prefixes))
        main.save()
        return main


class StringListSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return instance
