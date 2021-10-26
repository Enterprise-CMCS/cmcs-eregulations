from rest_framework import generics
from django.db.models import Prefetch, Q

from .models import (
    AbstractSupplementalContent,
    AbstractLocation,
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
