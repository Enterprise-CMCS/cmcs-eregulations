from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from regcore.models import Title, Part
from regcore.views import SettingsAuthentication

from regcore.serializers import (
    ContentsSerializer,
    TitleSerializer,
    VersionsSerializer,
)


class MultipleFieldLookupMixin(object):
    # must define lookup_fields mapping with entries like { "field_name": "url_parameter", ... }
    def get_object(self):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        filter = {}
        for field in self.lookup_fields:
            if self.kwargs.get(self.lookup_fields[field], None):
                filter[field] = self.kwargs[self.lookup_fields[field]]
        obj = get_object_or_404(queryset, **filter)
        self.check_object_permissions(self.request, obj)
        return obj


class ContentsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Title.objects.all()
    serializer_class = ContentsSerializer


class TitleViewSet(MultipleFieldLookupMixin, viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    lookup_fields = {"name": "title"}

    authentication_classes = [SettingsAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]


class VersionsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VersionsSerializer

    def get_queryset(self):
        title = self.kwargs.get("title")
        part = self.kwargs.get("part")
        return Part.objects.filter(title=title, name=part).order_by("-date")


class PartContentsViewSet(MultipleFieldLookupMixin, viewsets.ReadOnlyModelViewSet):
    # TODO: modify so ".../version/latest/..." returns the latest version
    # best accomplished after ordering can be set on Parts
    queryset = Part.objects.all()
    serializer_class = ContentsSerializer
    lookup_fields = {
        "title": "title",
        "name": "part",
        "date": "version",
    }
