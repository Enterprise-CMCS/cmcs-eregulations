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


class FrontPageTOCListSerializer(serializers.ListSerializer):
    def to_representation(self, stacks):
        toc = {}
        current = toc
        for stack in stacks:
            for i in stack:
                ident = ".".join(i["identifier"])
                if ident in current:
                    if "children" not in current[ident]:
                        current[ident]["children"] = {}
                    current = current[ident]["children"]
                else:
                    current[ident] = i
        return self.convert_to_list(toc)

    def convert_to_list(self, toc):
        toc = list(toc.values())
        for i in toc:
            if "children" in i:
                i["children"] = self.convert_to_list(i["children"])
        return toc


class FrontPageTOCSerializer(TOCSerializer):
    class Meta:
        list_serializer_class = FrontPageTOCListSerializer
