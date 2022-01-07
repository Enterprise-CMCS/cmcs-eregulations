from rest_framework import generics, serializers
from django.conf import settings

from rest_framework.response import Response

from django.db.models import Prefetch, Q

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import authentication
from rest_framework import exceptions

from .models import (
    AbstractSupplementalContent,
    AbstractLocation,
    Section,
    Subpart,
    Category,
    AbstractCategory, SupplementalContent
)

from .serializers import AbstractSupplementalContentSerializer


class SettingsUser:
    is_authenticated = False


class SettingsAuthentication(authentication.BasicAuthentication):
    def authenticate_credentials(self, userid, password, request=None):
        if userid == settings.HTTP_AUTH_USER and password == settings.HTTP_AUTH_PASSWORD:
            user = SettingsUser()
            user.is_authenticated = True
            return (user, None)
        raise exceptions.AuthenticationFailed('No such user')


class SupplementalContentView(generics.ListAPIView):
    serializer_class = AbstractSupplementalContentSerializer

    def get_queryset(self):
        title = self.kwargs.get("title")
        part = self.kwargs.get("part")
        section_list = self.request.GET.getlist("sections")
        subpart_list = self.request.GET.getlist("subparts")
        subjgrp_list = self.request.GET.getlist("subjectgroups")

        query = AbstractSupplementalContent.objects \
            .filter(
                Q(locations__section__section_id__in=section_list) |
                Q(locations__subpart__subpart_id__in=subpart_list) |
                Q(locations__subjectgroup__subject_group_id__in=subjgrp_list),
                approved=True,
                category__isnull=False,
                locations__title=title,
                locations__part=part,
            )\
            .prefetch_related(
                Prefetch(
                    'locations',
                    queryset=AbstractLocation.objects.filter(
                        Q(section__section_id__in=section_list) |
                        Q(subpart__subpart_id__in=subpart_list) |
                        Q(subjectgroup__subject_group_id__in=subjgrp_list),
                        title=title,
                        part=part,
                    )
                )
            ).distinct()
        return query


class SupplementalContentSectionsView(generics.CreateAPIView):
    authentication_classes = [SettingsAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        for section in request.data["sections"]:
            new_orphan_section, created = Section.objects.get_or_create(
                        title=section["title"],
                        part=section["part"],
                        section_id=section["section"]
                    )

        for subpart in request.data["subparts"]:
            new_subpart, created = Subpart.objects.get_or_create(
                        title=subpart["title"],
                        part=subpart["part"],
                        subpart_id=subpart["subpart"]
                    )

            for section in subpart["sections"]:
                new_section, created = Section.objects.update_or_create(
                            title=section["title"],
                            part=section["part"],
                            section_id=section["section"],
                            defaults={'parent': new_subpart}
                        )
        return Response({'error': False, 'content': request.data})

class PartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['title', 'part']


class PartsListView(generics.ListAPIView):
    serializer_class = PartSerializer

    def get_queryset(self):
        title = self.kwargs.get("title")
        return Section.objects.filter(title=title).order_by('part').distinct('part')


class SubPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subpart
        fields = ['id', 'subpart_id']


class SubPartsListView(generics.ListAPIView):
    serializer_class = SubPartSerializer

    def get_queryset(self):
        title = self.kwargs.get("title")
        part = self.kwargs.get("part")
        return Subpart.objects.filter(title=title, part=part)


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'section_id', ]


class SectionsListView(generics.ListAPIView):
    serializer_class = SectionSerializer

    def get_queryset(self):
        subPart = self.kwargs.get("subPart")
        title = self.kwargs.get("title")
        part = self.kwargs.get("part")
        if subPart:
            return Section.objects.filter(parent__id=subPart) if subPart != "ORPHAN" else Section.objects.filter(title=title, part=part, parent__id=None)
        else:
            return Section.objects.filter(title=title, part=part)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return AbstractCategory.objects.all().order_by('name')


class LocationField(serializers.RelatedField):
    def to_representation(self, value):
        return {'name': '%s' % value.__str__(), 'id': value.id}


class CategoryField(serializers.RelatedField):
    def to_representation(self, value):
        return '%s' % value.__str__()


class SupplementalContentSerializer(serializers.ModelSerializer):
    locations = LocationField(read_only=True, many=True)
    category = CategoryField(read_only=True)
    class Meta:
        model = SupplementalContent
        fields = ['id', 'description', 'name', 'url', 'category', 'locations']


class SupplementalContentListView(generics.ListAPIView):
    serializer_class = SupplementalContentSerializer

    def get_queryset(self):
        section = self.request.GET.get("section")
        category = self.request.GET.get("category")
        section = Section.objects.get(id=section)
        query = section.supplemental_content.values_list('id', flat=True)
        if category:
            query = query.filter(category_id=category)
        else:
            query = query.all()

        return SupplementalContent.objects.filter(id__in=query)
