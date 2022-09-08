from rest_framework import serializers


class FlatTOCSerializer(serializers.Serializer):
    type = serializers.CharField()
    label = serializers.CharField()
    parent = serializers.ListField(child=serializers.CharField(), allow_null=True, allow_empty=True)
    reserved = serializers.BooleanField()
    identifier = serializers.ListField(child=serializers.CharField())
    label_level = serializers.CharField()
    parent_type = serializers.CharField(allow_blank=True)
    descendant_range = serializers.ListField(child=serializers.CharField(), allow_null=True, allow_empty=True)
    label_description = serializers.CharField()


class TOCSerializer(FlatTOCSerializer):
    def get_fields(self):
        fields = super(TOCSerializer, self).get_fields()
        fields['children'] = serializers.ListField(child=TOCSerializer(), allow_null=True, allow_empty=True)
        return fields
