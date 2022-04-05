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


class NodeTypeSerializer(serializers.BaseSerializer):
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
            node["children"] = None
        return nodes


class PartSectionsSerializer(NodeTypeSerializer):
    node_type = "section"


class PartSubpartsSerializer(NodeTypeSerializer):
    node_type = "subpart"
