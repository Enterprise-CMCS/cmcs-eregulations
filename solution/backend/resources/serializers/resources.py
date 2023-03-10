import re
from rest_framework import serializers
from django.urls import reverse
from drf_spectacular.utils import extend_schema_field, OpenApiTypes
from django.db.models import Q

from resources.models import (
    SupplementalContent,
    FederalRegisterDocument,
    FederalRegisterDocumentGroup,
    ResourcesConfiguration,
    Category,
    AbstractCategory,
    Section,
    AbstractLocation,
)

from .locations import (
    SectionCreateSerializer,
    SectionRangeCreateSerializer,
    AbstractLocationPolymorphicSerializer,
    MetaLocationSerializer,
)
from .categories import AbstractCategoryPolymorphicSerializer, MetaCategorySerializer
from .mixins import HeadlineField, PolymorphicSerializer, PolymorphicTypeField
from .utils import ProxySerializerWrapper


class AbstractResourcePolymorphicSerializer(PolymorphicSerializer):
    def get_serializer_map(self):
        return {
            SupplementalContent: ("supplemental_content", SupplementalContentSerializer),
            FederalRegisterDocument: ("federal_register_doc", FederalRegisterDocumentSerializer),
        }


class AbstractResourceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    created_at = serializers.CharField()
    updated_at = serializers.CharField()
    approved = serializers.BooleanField()

    category = serializers.SerializerMethodField()
    locations = serializers.SerializerMethodField()

    type = PolymorphicTypeField()

    @extend_schema_field(MetaCategorySerializer.many(False))
    def get_category(self, obj):
        if self.context.get("category_details", True):
            return AbstractCategoryPolymorphicSerializer(obj.category).data
        return serializers.PrimaryKeyRelatedField(read_only=True).to_representation(obj.category)

    @extend_schema_field(MetaLocationSerializer.many(True))
    def get_locations(self, obj):
        if self.context.get("location_details", True):
            return AbstractLocationPolymorphicSerializer(obj.locations, many=True).data
        return serializers.PrimaryKeyRelatedField(read_only=True, many=True).to_representation(obj.locations.all())


class DateFieldSerializer(serializers.Serializer):
    date = serializers.CharField()


# Provides fields most often used in resources
class TypicalResourceFieldsSerializer(DateFieldSerializer):
    name = serializers.CharField()
    description = serializers.CharField()
    url = serializers.CharField()
    internalURL = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.STR)
    def get_internalURL(self, obj):
        return reverse('supplemental_content', kwargs={'id': obj.pk})


class SupplementalContentSerializer(AbstractResourceSerializer, TypicalResourceFieldsSerializer):
    name_headline = HeadlineField("supplementalcontent")
    description_headline = HeadlineField("supplementalcontent")


class SimpleFederalRegisterDocumentSerializer(AbstractResourceSerializer, TypicalResourceFieldsSerializer):
    docket_numbers = serializers.ListField(child=serializers.CharField())
    document_number = serializers.CharField()
    doc_type = serializers.CharField()
    correction = serializers.BooleanField()
    withdrawal = serializers.BooleanField()
    name_headline = HeadlineField("federalregisterdocument")
    description_headline = HeadlineField("federalregisterdocument")
    document_number_headline = HeadlineField("federalregisterdocument")


class FederalRegisterDocumentSerializer(SimpleFederalRegisterDocumentSerializer):
    related_docs = SimpleFederalRegisterDocumentSerializer(many=True, source="related_resources")

    def to_representation(self, instance):
        obj = super().to_representation(instance)
        if not self.context.get("fr_grouping", False):
            del obj["related_docs"]
            return obj
        docs = [obj] + obj["related_docs"]
        del obj["related_docs"]
        docs = sorted(docs, key=lambda i: i["date"] or "", reverse=True)
        docs[0]["related_docs"] = docs[1:]
        return docs[0]


class ResourceSearchSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.CharField()
    previous = serializers.CharField()
    results = AbstractResourcePolymorphicSerializer(many=True)


MetaResourceSerializer = ProxySerializerWrapper(
    component_name="MetaResourceSerializer",
    serializers=[SupplementalContentSerializer, FederalRegisterDocumentSerializer],
    resource_type_field_name=None,
)


class FederalRegisterDocumentCreateSerializer(serializers.Serializer):
    sections = SectionCreateSerializer(many=True, allow_null=True)
    section_ranges = SectionRangeCreateSerializer(many=True, allow_null=True, required=False)
    url = serializers.URLField(allow_blank=True, allow_null=True)
    description = serializers.CharField(allow_blank=True, allow_null=True)
    name = serializers.CharField(allow_blank=True, allow_null=True)
    name_sort = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    description_sort = serializers.CharField(allow_blank=True, allow_null=True, required=False)
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
        created = self.context.get("created", False)
        sections = validated_data.get("sections", []) or []
        section_ranges = validated_data.get("section_ranges", []) or []
        name = validated_data.get('name', instance.name)
        description = validated_data.get('description', instance.description)

        # set basic fields and group if instance is new
        if created:
            instance.url = validated_data.get('url', instance.url)
            instance.description = description
            instance.description_sort = self.naturalize(description)
            instance.name = name
            instance.name_sort = self.naturalize(name)
            instance.docket_numbers = validated_data.get('docket_numbers', instance.docket_numbers)
            instance.document_number = validated_data.get('document_number', instance.document_number)
            instance.date = validated_data.get('date', instance.date)
            instance.approved = validated_data.get('approved', instance.approved)
            instance.doc_type = validated_data.get('doc_type', instance.doc_type)
            instance.category = self.get_category()
            self.set_group(instance)

        # set the locations on the instance
        self.set_locations(instance, sections, section_ranges)

        # reapply changelog if instance is not new
        if not created:
            self.apply_changelog(instance)

        # save and return
        instance.save()
        return instance

    def naturalize(self, string):
        def naturalize_int_match(match):
            return '%08d' % (int(match.group(0)),)

        if string:
            string = re.sub(r'\d+', naturalize_int_match, string.lower().strip())

        return string

    def get_location_objects(self, locations):
        queries = []
        for i in locations:
            t = i["type"]
            queries.append(Q(title=i["title"]) & Q(part=i["part"]) & Q(**{f"{t}__{t}_id": i[f"{t}_id"]}))
        if not queries:
            return []
        q = queries[0]
        for i in queries[1:]:
            q |= i
        return AbstractLocation.objects.filter(q).select_subclasses()

    def apply_changelog(self, instance):
        all_additions = []
        all_removals = []
        for change in instance.location_history:
            additions = [i.copy() for i in change["additions"] + change["bulk_adds"]]
            removals = [i.copy() for i in change["removals"]]
            for i in additions + removals:
                del i["id"]
            for i in additions:
                all_removals.remove(i) if i in all_removals else all_additions.append(i)
            for i in removals:
                all_additions.remove(i) if i in all_additions else all_removals.append(i)
        instance.locations.remove(*self.get_location_objects(all_removals))
        instance.locations.add(*self.get_location_objects(all_additions))

    def set_locations(self, instance, raw_sections, raw_ranges):
        locations = []
        for loc in raw_sections:
            title = loc["title"]
            part = loc["part"]
            section_id = loc["section_id"]
            location, _ = Section.objects.get_or_create(title=title, part=part, section_id=section_id)
            location.save()
            locations.append(location)

        for loc_range in raw_ranges:
            title = loc_range['title']
            part = loc_range['part']
            first_section = loc_range['first_sec']
            last_section = loc_range['last_sec']
            Section.objects.get_or_create(title=title, part=part, section_id=first_section)
            Section.objects.get_or_create(title=title, part=part, section_id=last_section)
            sections = Section.objects.filter(title=title, part=part, section_id__range=(first_section, last_section))
            locations.extend(list(sections))
        instance.locations.set(locations)

    def set_group(self, instance):
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
