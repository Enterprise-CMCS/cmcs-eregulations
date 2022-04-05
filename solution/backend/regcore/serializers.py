from rest_framework import serializers

from regcore.models import Title, Part


class ContentsSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return instance.toc


class TitlesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ("id", "name", "last_updated")


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = "__all__"


class PartsSerialier(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = ("id", "name", "date", "last_updated", "depth", "title_object")


class VersionsSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return instance.date


# Inherit from this class to return a flat list of specific types of nodes within the part
# You must specify a node_type
class NodeTypeSerializer(serializers.BaseSerializer):
    remove_fields = []

    def find_nodes(self, structure):
        nodes = []
        for child in structure["children"]:
            if child["type"] == self.node_type:
                nodes.append(child)
            if child["children"]:
                nodes = nodes + self.find_nodes(child)
        return nodes

    def to_representation(self, instance):
        part = instance.structure
        for _ in range(instance.depth):
            part = part["children"][0]
        nodes = self.find_nodes(part)
        for node in nodes:
            for field in self.remove_fields + ["children", "type"]:
                del node[field]
        return nodes


class PartSectionsSerializer(NodeTypeSerializer):
    node_type = "section"
    remove_fields = ["descendant_range"]


class PartSubpartsSerializer(NodeTypeSerializer):
    node_type = "subpart"
