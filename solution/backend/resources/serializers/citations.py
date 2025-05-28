from functools import partial

from rest_framework import serializers

from regulations.utils import (
    SECTION_REGEX,
    replace_section,
)
from regulations.utils.link_statutes import replace_usc_citation
from resources.models import (
    Section,
    Subpart,
)

from .polymorphic import (
    PolymorphicSerializer,
    PolymorphicTypeField,
    ProxySerializerWrapper,
)


class AbstractCitationSerializer(PolymorphicSerializer):
    def get_serializer_map(self):
        return {
            Section: ("section", SectionSerializer),
            Subpart: ("subpart", SubpartSerializer),
        }


class CitationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.IntegerField()
    part = serializers.IntegerField()
    type = PolymorphicTypeField()


class SectionSerializer(CitationSerializer):
    section_id = serializers.IntegerField()


class SubpartSerializer(CitationSerializer):
    subpart_id = serializers.CharField()


class SectionWithParentSerializer(SectionSerializer):
    parent = SubpartSerializer()


class SubpartWithChildrenSerializer(SubpartSerializer):
    children = SectionSerializer(many=True)


class SectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = "__all__"


class SectionRangeCreateSerializer(serializers.Serializer):
    title = serializers.CharField()
    part = serializers.CharField()
    first_sec = serializers.IntegerField()
    last_sec = serializers.IntegerField()


MetaCitationSerializer = ProxySerializerWrapper(
    component_name="MetaCitationSerializer",
    resource_type_field_name="type",
    serializers=[
        SectionSerializer,
        SubpartSerializer,
    ],
)


class ActCitationSerializer(serializers.Serializer):
    act = serializers.CharField()
    section = serializers.CharField()
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        conversions = self.context.get("link_conversions")
        if conversions and obj["act"] and obj["section"]:
            return SECTION_REGEX.sub(
                partial(
                    replace_section,
                    act=obj["act"],
                    link_conversions=conversions,
                    exceptions=[],
                    generate_url_only=True
                ),
                obj["section"]
            )
        return None


class UscCitationSerializer(serializers.Serializer):
    title = serializers.CharField()
    section = serializers.CharField()
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        if obj["title"] and obj["section"]:
            return SECTION_REGEX.sub(
                partial(
                    replace_usc_citation,
                    title=obj["title"],
                    exceptions=[],
                    generate_url_only=True
                ),
                obj["section"]
            )
        return None
