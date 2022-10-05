from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field, PolymorphicProxySerializer

from resources.models import Section, Subpart
from .mixins import PolymorphicSerializer
from .utils import ProxySerializerWrapper


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


MetaLocationSerializer = ProxySerializerWrapper(
    component_name="MetaLocationSerializer",
    serializers=[SubpartSerializer, SectionSerializer],
    resource_type_field_name="type",
)


class FullSectionSerializer(SectionSerializer):
    parent = serializers.SerializerMethodField()

    @extend_schema_field(MetaLocationSerializer.many(False))
    def get_parent(self, obj):
        return AbstractLocationPolymorphicSerializer(obj.parent).data


class FullSubpartSerializer(SubpartSerializer):
    children = serializers.SerializerMethodField()

    @extend_schema_field(MetaLocationSerializer.many(True))
    def get_children(self, obj):
        return AbstractLocationPolymorphicSerializer(obj.children, many=True).data


class SectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = "__all__"


class SectionRangeCreateSerializer(serializers.Serializer):
    title = serializers.CharField()
    part = serializers.CharField()
    first_sec = serializers.IntegerField()
    last_sec = serializers.IntegerField()
