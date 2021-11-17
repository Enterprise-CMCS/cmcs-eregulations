from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from django.db.models import Prefetch, Q
from django.core import serializers

from .models import (
    AbstractSupplementalContent,
    AbstractLocation,
    Section,
    Subpart,
)

from .serializers import AbstractSupplementalContentSerializer


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
    def create(self, request, *args, **kwargs):
        sections = []
        subparts = []
        for section in request.data["sections"]:
            try:
                new_section, created = Section.objects.get_or_create(
                            title=section["title"],
                            part=section["part"],
                            section_id=section["section"]
                        )
                sections.append(new_section)
            except Exception:
                return Response({'error': True, 'content': 'Exception!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        for subpart in request.data["subparts"]:
            try:
                new_subpart, created = Subpart.objects.get_or_create(
                            title=subpart["title"],
                            part=subpart["part"],
                            subpart_id=subpart["subpart"]
                        )
                subparts.append(new_subpart)
            except Exception:
                return Response({'error': True, 'content': 'Exception!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            for section in subpart["sections"]:
                try:
                    new_section, created = Section.objects.get_or_create(
                                title=section["title"],
                                part=section["part"],
                                section_id=section["section"]
                            )
                    sections.append(new_section)
                except Exception:
                    return Response({'error': True, 'content': 'Exception!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        res = serializers.serialize('json', [new_section, ])
        return Response({'error': False, 'content': res})
