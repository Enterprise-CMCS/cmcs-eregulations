from rest_framework import generics
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
