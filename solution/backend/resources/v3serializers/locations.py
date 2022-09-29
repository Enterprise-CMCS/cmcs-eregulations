from rest_framework import serializers

from resources.models import Section, Subpart
from .mixins import PolymorphicSerializer


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

    class Meta:
        model = Section


class FullSectionSerializer(SectionSerializer):
    parent = AbstractLocationPolymorphicSerializer()


class FullSubpartSerializer(SubpartSerializer):
    children = AbstractLocationPolymorphicSerializer(many=True)


class SectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = "__all__"


class SectionRangeCreateSerializer(serializers.Serializer):
    title = serializers.CharField()
    part = serializers.CharField()
    first_sec = serializers.IntegerField()
    last_sec = serializers.IntegerField()
