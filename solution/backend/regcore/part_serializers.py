from rest_framework import serializers
from drf_spectacular.utils import PolymorphicProxySerializer, extend_schema_field


class NodeChildrenField(serializers.DictField):
    def get_serializer_map(self):
        raise NotImplementedError()

    def to_representation(self, obj):
        node_type = obj["node_type"]
        if node_type in self.get_serializer_map():
            return self.get_serializer_map()[node_type](instance=obj, context=self.context).data
        return "Serializer not available"


# Base serializers for node types


class PartNodeSerializer(serializers.Serializer):
    node_type = serializers.CharField()


class ContentNodeSerializer(PartNodeSerializer):
    content = serializers.CharField()


class HeaderNodeSerializer(PartNodeSerializer):
    header = serializers.CharField()


# Bottom-level nodes (e.g. paragraph, image)


class ParagraphSerializer(PartNodeSerializer):
    text = serializers.CharField()
    label = serializers.ListField(child=serializers.CharField())
    marker = serializers.ListField(child=serializers.CharField())


class EffectiveDateNoteSerializer(HeaderNodeSerializer, ContentNodeSerializer):
    pass


class HeadingSerializer(ContentNodeSerializer):
    pass


class DivisionSerializer(ContentNodeSerializer):
    pass


class FootNoteSerializer(ContentNodeSerializer):
    pass


class ImageSerializer(PartNodeSerializer):
    src = serializers.CharField()


class FlushParagraphSerializer(ContentNodeSerializer):
    pass


class SectionAuthoritySerializer(ContentNodeSerializer):
    pass


class EdNoteSerializer(HeaderNodeSerializer, ContentNodeSerializer):
    pass


class AuthoritySerializer(HeaderNodeSerializer, ContentNodeSerializer):
    pass


class SourceSerializer(HeaderNodeSerializer, ContentNodeSerializer):
    pass


class CitationSerializer(ContentNodeSerializer):
    pass


class ExtractSerializer(ContentNodeSerializer):
    pass


# Second-level serializers (e.g. subpart, section, appendix)


@extend_schema_field(
    PolymorphicProxySerializer(
        component_name="SectionChildrenField",
        serializers=[
            ParagraphSerializer,
            FlushParagraphSerializer,
            ImageSerializer,
            ExtractSerializer,
            CitationSerializer,
            SectionAuthoritySerializer,
            FootNoteSerializer,
            DivisionSerializer,
            EffectiveDateNoteSerializer,
        ],
        resource_type_field_name="node_type",
    )
)
class SectionChildrenField(NodeChildrenField):
    def get_serializer_map(self):
        return {
            "Paragraph": ParagraphSerializer,
            "FlushParagraph": FlushParagraphSerializer,
            "Image": ImageSerializer,
            "Extract": ExtractSerializer,
            "Citation": CitationSerializer,
            "SectionAuthority": SectionAuthoritySerializer,
            "FootNote": FootNoteSerializer,
            "Division": DivisionSerializer,
            "EffectiveDateNote": EffectiveDateNoteSerializer,
        }


class SectionSerializer(PartNodeSerializer):
    title = serializers.CharField()
    label = serializers.ListField(child=serializers.CharField())
    children = serializers.ListField(child=SectionChildrenField())


@extend_schema_field(
    PolymorphicProxySerializer(
        component_name="AppendixChildrenField",
        serializers=[ParagraphSerializer, HeadingSerializer],
        resource_type_field_name="node_type",
    )
)
class AppendixChildrenField(NodeChildrenField):
    def get_serializer_map(self):
        return {
            "Paragraph": ParagraphSerializer,
            "Heading": HeadingSerializer,
        }


class AppendixSerializer(PartNodeSerializer):
    title = serializers.CharField()
    label = serializers.ListField(child=serializers.CharField())
    children = serializers.ListField(child=AppendixChildrenField())


@extend_schema_field(
    PolymorphicProxySerializer(
        component_name="SubjectGroupChildrenField",
        serializers=[SectionSerializer, FootNoteSerializer],
        resource_type_field_name="node_type",
    )
)
class SubjectGroupChildrenField(NodeChildrenField):
    def get_serializer_map(self):
        return {
            "SECTION": SectionSerializer,
            "FootNote": FootNoteSerializer,
        }


class SubjectGroupSerializer(PartNodeSerializer):
    title = serializers.CharField()
    label = serializers.ListField(child=serializers.CharField())
    children = serializers.ListField(child=SubjectGroupChildrenField())


@extend_schema_field(
    PolymorphicProxySerializer(
        component_name="SubpartChildrenField",
        serializers=[
            SectionSerializer,
            SubjectGroupSerializer,
            AppendixSerializer,
            SourceSerializer,
        ],
        resource_type_field_name="node_type",
    )
)
class SubpartChildrenField(NodeChildrenField):
    def get_serializer_map(self):
        return {
            "SECTION": SectionSerializer,
            "SUBJGRP": SubjectGroupSerializer,
            "APPENDIX": AppendixSerializer,
            "Source": SourceSerializer,
        }


class SubpartSerializer(PartNodeSerializer):
    title = serializers.CharField()
    label = serializers.ListField(child=serializers.CharField())
    children = serializers.ListField(child=SubpartChildrenField())


# First-level serializer for part objects


@extend_schema_field(
    PolymorphicProxySerializer(
        component_name="PartChildrenField",
        serializers=[SubpartSerializer, SectionSerializer],
        resource_type_field_name="node_type",
    )
)
class PartChildrenField(NodeChildrenField):
    def get_serializer_map(self):
        return {
            "SUBPART": SubpartSerializer,
            "SECTION": SectionSerializer,
        }


# TODO: Remove V3 in front of serializer name (currently causes Swagger conflict with V2)
class V3PartSerializer(PartNodeSerializer):
    label = serializers.ListField(child=serializers.CharField())
    title = serializers.CharField()
    authority = AuthoritySerializer()
    source = SourceSerializer()
    editorial_note = EdNoteSerializer()
    children = serializers.ListField(child=PartChildrenField())
