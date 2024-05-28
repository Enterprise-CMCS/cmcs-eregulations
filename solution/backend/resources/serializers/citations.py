from rest_framework import serializers

from resources.models import (
    NewSection,
    NewSubpart,
)

from .polymorphic import (
    PolymorphicSerializer,
    PolymorphicTypeField,
)


class AbstractCitationSerializer(PolymorphicSerializer):
    def get_serializer_map(self):
        return {
            NewSection: ("section", SectionSerializer),
            NewSubpart: ("subpart", SubpartSerializer),
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
