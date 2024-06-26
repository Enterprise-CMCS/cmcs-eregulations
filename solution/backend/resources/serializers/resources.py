from rest_framework import serializers

from resources.models import (
    FederalRegisterLink,
    InternalFile,
    InternalLink,
    PublicLink,
)

from .categories import AbstractCategorySerializer
from .citations import AbstractCitationSerializer
from .polymorphic import (
    PolymorphicSerializer,
    PolymorphicTypeField,
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
