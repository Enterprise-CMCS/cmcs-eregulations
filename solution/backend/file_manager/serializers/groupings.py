from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from common.serializers.clean import PolymorphicSerializer, PolymorphicTypeField
from common.utils import ProxySerializerWrapper
from file_manager.models import DocumentType, RepositoryCategory, RepositorySubCategory, Subject


class DocumentTypeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()

    class Meta:
        model = DocumentType


class SubjectSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    short_name = serializers.CharField()
    abbreviation = serializers.CharField()


class SubjectDetailsSerializer(SubjectSerializer):
    content = serializers.SerializerMethodField()
    internal_content = serializers.IntegerField()
    external_content = serializers.IntegerField()

    def get_content(self, obj):
        return obj.content.count()

    class Meta:
        model = Subject


class AbstractRepositoryCategoryPolymorphicSerializer(PolymorphicSerializer):
    def get_serializer_map(self):
        return {
            RepositoryCategory: ("repositorycategory", RepositoryCategorySerializer),
            RepositorySubCategory: ("repositorysubcategory", RepositorySubCategorySerializer),
        }


class RepositoryCategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    order = serializers.IntegerField()
    show_if_empty = serializers.BooleanField()
    type = PolymorphicTypeField()


class RepositorySubCategorySerializer(RepositoryCategorySerializer):
    parent = serializers.SerializerMethodField()

    @extend_schema_field(RepositoryCategorySerializer)
    def get_parent(self, obj):
        if self.context.get("parent_details", True):
            return RepositoryCategorySerializer().to_representation(obj.parent)
        return serializers.PrimaryKeyRelatedField(read_only=True).to_representation(obj.parent)


MetaRepositoryCategorySerializer = ProxySerializerWrapper(
    component_name="MetaCategorySerializer",
    serializers=[RepositoryCategorySerializer, RepositorySubCategorySerializer],
    resource_type_field_name="type",
)


class RepositoryCategoryTreeSerializer(RepositoryCategorySerializer):
    sub_categories = RepositoryCategorySerializer(many=True)
