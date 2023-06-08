from django.http import Http404
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


class TOCListSerializer(serializers.ListSerializer):
    def create_tree(self, stacks):
        tree = {}
        for stack in stacks:
            current = tree
            for i in stack:
                ident = ".".join(i["identifier"])
                if ident not in current:
                    current[ident] = i
                if "children" not in current[ident]:
                    current[ident]["children"] = {}
                current = current[ident]["children"]
        return tree

    def convert_to_list(self, tree):
        tree = list(tree.values())
        for i in tree:
            if "children" in i:
                i["children"] = self.convert_to_list(i["children"])
        tree = [TOCSerializer(data=i) for i in tree]
        for i in tree:
            i.is_valid(raise_exception=True)
        return [i.data for i in tree]


class TitleTOCListSerializer(TOCListSerializer):
    def to_representation(self, stacks):
        toc = self.convert_to_list(self.create_tree(stacks))
        if len(toc) < 1:
            raise Http404()
        return toc[0]

    @property
    def data(self):
        ret = serializers.BaseSerializer.data.fget(self)
        return serializers.ReturnDict(ret, serializer=self)


class TitleTOCSerializer(TOCSerializer):
    class Meta:
        list_serializer_class = TitleTOCListSerializer


class FrontPageTOCListSerializer(TOCListSerializer):
    def to_representation(self, stacks):
        return self.convert_to_list(self.create_tree(stacks))


class FrontPageTOCSerializer(TOCSerializer):
    class Meta:
        list_serializer_class = FrontPageTOCListSerializer
