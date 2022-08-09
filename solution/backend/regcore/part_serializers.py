from rest_framework import serializers


class NodeTypeSerializer(serializers.Serializer):
    def get_serializer_map(self):
        raise NotImplementedError()

    def to_representation(self, instance):
        node_type = instance["node_type"]
        if node_type in self.get_serializer_map():
            data = self.get_serializer_map()[node_type](instance=instance, context=self.context).data
            return data
        return "Serializer not available"


# Note this serializer is only used for generating OpenAPI docs
class MiniPartNodeSwaggerSerializer(serializers.Serializer):
    node_type = serializers.CharField()
    header = serializers.CharField()
    content = serializers.CharField()


# Note this serializer is only used for generating OpenAPI docs
class PartNodeSwaggerSerializer(MiniPartNodeSwaggerSerializer):
    label = serializers.ListField(child=serializers.CharField())
    title = serializers.CharField()
    authority = MiniPartNodeSwaggerSerializer()
    source = MiniPartNodeSwaggerSerializer()
    editorial_node = MiniPartNodeSwaggerSerializer()
    children = MiniPartNodeSwaggerSerializer(many=True)


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

class SectionChildrenSerializer(NodeTypeSerializer):
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
    children = SectionChildrenSerializer(many=True)  


class AppendixChildrenSerializer(NodeTypeSerializer):
    def get_serializer_map(self):
        return {
            "Paragraph": ParagraphSerializer,
            "Heading": HeadingSerializer,
        }


class AppendixSerializer(PartNodeSerializer):
    title = serializers.CharField()
    label = serializers.ListField(child=serializers.CharField())
    children = AppendixChildrenSerializer(many=True)  


class SubjectGroupChildrenSerializer(NodeTypeSerializer):
    def get_serializer_map(self):
        return {
            "SECTION": SectionSerializer,
            "FootNote": FootNoteSerializer,
        }


class SubjectGroupSerializer(PartNodeSerializer):
    title = serializers.CharField()
    label = serializers.ListField(child=serializers.CharField())
    children = SubjectGroupChildrenSerializer(many=True)    


class SubpartChildrenSerializer(NodeTypeSerializer):
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
    children = SubpartChildrenSerializer(many=True)


# First-level serializer for part objects

class PartChildrenSerializer(NodeTypeSerializer):
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
    children = PartChildrenSerializer(many=True)
