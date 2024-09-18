import re

from django.db.models import Q
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from resources.models import (
    AbstractCitation,
    AbstractPublicCategory,
    FederalRegisterLink,
    InternalFile,
    InternalLink,
    PublicCategory,
    PublicLink,
    ResourceGroup,
    ResourcesConfiguration,
    Section,
)

from .categories import AbstractCategorySerializer
from .citations import (
    AbstractCitationSerializer,
    SectionCreateSerializer,
    SectionRangeCreateSerializer,
)
from .polymorphic import (
    PolymorphicSerializer,
    PolymorphicTypeField,
    ProxySerializerWrapper,
)
from .subjects import SubjectSerializer


class AbstractResourceSerializer(PolymorphicSerializer):
    def get_serializer_map(self):
        return {
            PublicLink: ("public_link", PublicLinkSerializer),
            FederalRegisterLink: ("federal_register_link", FederalRegisterLinkSerializer),
            InternalLink: ("internal_link", InternalLinkSerializer),
            InternalFile: ("internal_file", InternalFileSerializer),
        }


class FederalRegisterLinkCreateSerializer(serializers.Serializer):
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
    approved = serializers.BooleanField(required=False, default=True)
    id = serializers.CharField(required=False)
    doc_type = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    raw_text_url = serializers.CharField(allow_blank=True, allow_null=True)

    def get_category(self):
        config = ResourcesConfiguration.objects.first()
        category = config.fr_link_category
        if not category:
            try:
                category = AbstractPublicCategory.objects.get(name="Federal Register Links")
            except AbstractPublicCategory.DoesNotExist:
                category = PublicCategory.objects.create(name="Federal Register Links")
            config.fr_link_category = category
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
        name = validated_data.get('name', instance.document_id)
        description = validated_data.get('description', instance.title)

        # set basic fields and group if instance is new
        if created:
            instance.url = validated_data.get('url', instance.url)
            instance.title = description
            instance.title_sort = self.naturalize(description)
            instance.document_id = name
            instance.document_id_sort = self.naturalize(name)
            instance.docket_numbers = validated_data.get('docket_numbers', instance.docket_numbers)
            instance.document_number = validated_data.get('document_number', instance.document_number)
            instance.date = validated_data.get('date', instance.date)
            instance.approved = validated_data.get('approved', instance.approved)
            instance.action_type = validated_data.get('doc_type', instance.action_type)
            instance.category = self.get_category()
            self.set_group(instance)

        instance.extract_url = validated_data.get("raw_text_url", "")

        # set the locations on the instance
        self.set_locations(instance, sections, section_ranges)

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
        return AbstractCitation.objects.filter(q).select_subclasses()

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
        instance.cfr_citations.set(locations)

    def set_group(self, instance):
        prefixes = []
        for i in instance.docket_numbers:
            d = i.split("-")
            if len(d) > 1:
                prefixes.append("-".join(d[0:-1]) + "-")
        if len(prefixes) > 0:
            groups = ResourceGroup.objects.filter(common_identifiers__overlap=prefixes)
            if len(groups) == 0:
                group = ResourceGroup.objects.create(common_identifiers=prefixes)
            else:
                group = self.combine_groups(groups) if len(groups) > 1 else groups[0]
            group.common_identifiers = list(set(group.common_identifiers + prefixes))
            group.save()
            instance.resource_groups.set([group])

    def combine_groups(self, groups):
        main = groups[0]
        docs = main.resources.all()
        prefixes = main.common_identifiers
        for group in groups[1:]:
            docs |= group.resources.all()
            prefixes += group.common_identifiers
            group.delete()
        main.resources.set(docs.distinct())
        main.common_identifiers = list(set(prefixes))
        main.save()
        return main


class ResourceSerializer(serializers.Serializer):
    type = PolymorphicTypeField()
    id = serializers.IntegerField()
    created_at = serializers.CharField()
    updated_at = serializers.CharField()
    approved = serializers.BooleanField()
    category = AbstractCategorySerializer()
    cfr_citations = AbstractCitationSerializer(many=True)
    subjects = SubjectSerializer(many=True)
    document_id = serializers.CharField()
    title = serializers.CharField()
    date = serializers.CharField()
    url = serializers.CharField()
    related_resources = serializers.SerializerMethodField()

    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_related_resources(self, obj):
        if self.context.get("show_related", False):
            return AbstractResourceSerializer(instance=obj.related_resources, many=True).data
        return None


class PublicResourceSerializer(ResourceSerializer):
    pass


class InternalResourceSerializer(ResourceSerializer):
    summary = serializers.CharField()


class PublicLinkSerializer(PublicResourceSerializer):
    pass


class FederalRegisterLinkSerializer(PublicResourceSerializer):
    docket_numbers = serializers.ListField(child=serializers.CharField())
    document_number = serializers.CharField()
    correction = serializers.BooleanField()
    withdrawal = serializers.BooleanField()
    action_type = serializers.CharField()


class InternalLinkSerializer(InternalResourceSerializer):
    pass


class InternalFileSerializer(InternalResourceSerializer):
    file_name = serializers.CharField()
    file_type = serializers.CharField()
    uid = serializers.CharField()


class StringListSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return instance


MetaResourceSerializer = ProxySerializerWrapper(
    component_name="MetaResourceSerializer",
    resource_type_field_name="type",
    serializers=[
        PublicLinkSerializer,
        FederalRegisterLinkSerializer,
        InternalLinkSerializer,
        InternalFileSerializer,
    ],
)


MetaPublicResourceSerializer = ProxySerializerWrapper(
    component_name="MetaPublicResourceSerializer",
    resource_type_field_name="type",
    serializers=[
        PublicLinkSerializer,
        FederalRegisterLinkSerializer,
    ],
)


MetaInternalResourceSerializer = ProxySerializerWrapper(
    component_name="MetaInternalResourceSerializer",
    resource_type_field_name="type",
    serializers=[
        InternalLinkSerializer,
        InternalFileSerializer,
    ],
)
