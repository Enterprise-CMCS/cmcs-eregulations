import re
from functools import partial

from drf_spectacular.utils import extend_schema
from rest_framework import serializers, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from common.api import OpenApiQueryParameter
from common.patterns import (
    LINKED_PARAGRAPH_REGEX,
    SECTION_ID_REGEX,
)
from regulations.models import StatuteLinkConverter
from regulations.utils import (
    STATUTE_REF_REGEX,
    LinkConversionsMixin,
    replace_sections,
)


class StatuteLinkConverterSerializer(serializers.Serializer):
    section = serializers.CharField()
    title = serializers.IntegerField()
    usc = serializers.CharField()
    act = serializers.CharField()
    name = serializers.CharField()
    statute_title = serializers.IntegerField()
    statute_title_roman = serializers.CharField()
    source_url = serializers.CharField()


@extend_schema(
    tags=["regulations/statutes"],
    description="Retrieve a list of Statute Link Converters for a given act or all acts.",
    parameters=[
        OpenApiQueryParameter("act", "The act to filter down to.", str, False),
        OpenApiQueryParameter("title", "The title to filter down to. Act must be specified for this.", str, False),
    ],
)
class StatuteLinkConverterViewSet(viewsets.ReadOnlyModelViewSet):
    model = StatuteLinkConverter
    serializer_class = StatuteLinkConverterSerializer

    def get_queryset(self):
        act = self.request.GET.get("act", None)
        title = self.request.GET.get("title", None)
        if title and not act:
            raise ValidationError("You may specify either an act by itself, or an act and a title, but not a title by itself.")
        queryset = self.model.objects.all()
        if act:
            queryset = queryset.filter(act__iexact=act)
        if title:
            queryset = queryset.filter(statute_title__iexact=title)
        return queryset.order_by("act", "statute_title", "usc_sort")


class ActListSerializer(serializers.Serializer):
    act = serializers.CharField()
    title = serializers.IntegerField(source="statute_title")
    title_roman = serializers.CharField(source="statute_title_roman")


@extend_schema(
    tags=["regulations/statutes"],
    description="Retrieve a list of all acts and their titles. Compiled from internal Statute Link Converters.",
)
class ActListViewSet(viewsets.ReadOnlyModelViewSet):
    model = StatuteLinkConverter
    serializer_class = ActListSerializer

    def get_queryset(self):
        return self.model.objects\
            .exclude(act__isnull=True)\
            .exclude(act__exact='')\
            .exclude(statute_title__isnull=True)\
            .order_by("act", "statute_title")\
            .distinct("act", "statute_title")


class GetStatuteLinkAPIView(LinkConversionsMixin, APIView):
    def get(self, request):
        link_conversions = self.get_link_conversions()
        pattern_param = self.request.query_params.get("pattern", None)
        pattern_string = f"Section {pattern_param} of the Social Security Act" if pattern_param else None

        if not pattern_string:
            raise ValidationError("You must enter a statute.")

        result_link = STATUTE_REF_REGEX.sub(
                partial(replace_sections, link_conversions=link_conversions, exceptions={}),
                pattern_string
        )

        if result_link == pattern_string:
            raise ValidationError("No statute link found for the provided pattern.")

        HREF_CONTENTS_PATTERN = r"href=['\"]([^'\"]*)['\"]"
        HREF_CONTENTS_REGEX = re.compile(HREF_CONTENTS_PATTERN, re.IGNORECASE)

        section_id_match = SECTION_ID_REGEX.search(pattern_param)

        if section_id_match:
            section_id = section_id_match.group(1).strip()
            usc_id = link_conversions.get("Social Security Act", {}).get(section_id, {}).get("usc", "")
            if usc_id:
                usc_citation_string = rf"42 U.S.C {usc_id}"
                linked_paragraph_match = LINKED_PARAGRAPH_REGEX.search(pattern_param)
                if linked_paragraph_match:
                    usc_citation_string += linked_paragraph_match.group(1)
                    section_id += linked_paragraph_match.group(1)
            else:
                usc_citation_string = ""
        else:
            usc_citation_string = ""

        link_match = HREF_CONTENTS_REGEX.search(result_link)
        if link_match:
            raw_link = link_match.group(1).strip()
        else:
            raw_link = ""

        return Response({
            "input": pattern_param,
            "link": raw_link,
            "section_citation": rf"Section {section_id} of the Social Security Act" if section_id else "",
            "usc_citation": usc_citation_string,
        })
