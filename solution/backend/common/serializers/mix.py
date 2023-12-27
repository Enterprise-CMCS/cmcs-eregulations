from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from file_manager.serializers.groupings import AbstractRepositoryCategoryPolymorphicSerializer
from resources.serializers.categories import AbstractCategoryPolymorphicSerializer, MetaCategorySerializer
from resources.serializers.locations import AbstractLocationPolymorphicSerializer, MetaLocationSerializer


class DetailsSerializer(serializers.Serializer):
    @extend_schema_field(MetaLocationSerializer.many(True))
    def get_locations(self, obj):
        if self.context['request'].GET.get("location_details") == 'true':
            return AbstractLocationPolymorphicSerializer(obj.locations.all(), many=True).data
        return serializers.PrimaryKeyRelatedField(read_only=True, many=True).to_representation(obj.locations.all())

    @extend_schema_field(MetaCategorySerializer.many(False))
    def get_category(self, obj):
        if self.context['request'].GET.get("category_details") == 'true':
            if obj.category:
                return AbstractCategoryPolymorphicSerializer(obj.category).data
            elif obj.upload_category:
                return AbstractRepositoryCategoryPolymorphicSerializer(obj.upload_category).data
        return serializers.PrimaryKeyRelatedField(read_only=True).to_representation(obj)
