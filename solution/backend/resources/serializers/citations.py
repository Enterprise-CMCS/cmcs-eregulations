from rest_framework import serializers

from resources.models import (
    Section,
    Subpart,
)

from .polymorphic import (
    PolymorphicSerializer,
    PolymorphicTypeField,
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
