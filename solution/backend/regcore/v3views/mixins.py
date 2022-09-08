from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from .utils import OpenApiPathParameter

from regcore.models import Part
from regcore.serializers.toc import FlatTOCSerializer


# must define lookup_fields mapping with entries like { "field_name": "url_parameter", ... }
class MultipleFieldLookupMixin(object):
    def get_object(self):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        filter = {}
        latest_field = None
        for field, param in self.lookup_fields.items():
            value = self.kwargs.get(param, None)
            if param == "version" and value == "latest":
                latest_field = field
            elif value:
                filter[field] = value
        return queryset.filter(**filter).latest(latest_field) if latest_field else get_object_or_404(queryset, **filter)


# Inherit from this class to retrieve attributes from a specific version of a part
# You must specify a serializer_class
# Must also inherit from a Django REST Framework viewset (e.g. "viewsets.ReadOnlyModelViewSet")
class PartPropertiesMixin(MultipleFieldLookupMixin):
    PARAMETERS = [
        OpenApiPathParameter("title", "Title where Part is contained, e.g. 42.", int),
        OpenApiPathParameter("part", "Part of interest, e.g. 433.", int),
        OpenApiPathParameter("version", "Version of the Part. Must be in YYYY-MM-DD format (e.g. 2021-01-31), "
                             "or \"latest\" to retrieve the most recent version.", str),
    ]

    queryset = Part.objects.all()
    lookup_fields = {
        "title": "title",
        "name": "part",
        "date": "version",
    }


# Inherit from this class to retrieve a flat list of specific types of nodes within a part's structure
# You must specify a node_type
# Must also inherit from a Django REST Framework viewset (e.g. "viewsets.ReadOnlyModelViewSet")
class PartStructureNodesMixin(PartPropertiesMixin):
    serializer_class = FlatTOCSerializer

    def find_nodes(self, structure):
        nodes = []
        for child in structure["children"]:
            if child["type"] == self.node_type:
                nodes.append(child)
            if child["children"]:
                nodes = nodes + self.find_nodes(child)
        return nodes

    def retrieve(self, request, *args, **kwargs):
        nodes = self.find_nodes(self.get_object().toc)
        return Response(self.serializer_class(nodes, many=True).data)


# For retrieving a specific node from within a document tree structure
# Must define "node_type" as a string representing the value of "node_type" in the JSON
# Must define "label_index" as an integer representing the index in the label to identify the node
# Must define "parameter" as the URL parameter to use for identifying the node
# Must define "serializer_class"
# Must also inherit from a Django REST Framework viewset (e.g. "viewsets.ReadOnlyModelViewSet")
class NodeFinderMixin(PartPropertiesMixin):
    def retrieve(self, request, *args, **kwargs):
        node = kwargs.get(self.parameter, None)
        document = self.get_object().document
        node_content = self.find_node(document["children"], node)
        if not node_content:
            raise Http404()
        serializer = self.serializer_class(node_content)
        return Response(serializer.data)

    def find_node(self, node_children, node):
        for i in node_children:
            if i["node_type"] == self.node_type:
                if i["label"][self.label_index] == node:
                    return i
                continue
            if "children" in i:
                s = self.find_node(i["children"], node)
                if s:
                    return s
        return None
