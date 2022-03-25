from django.http import JsonResponse
from rest_framework import generics, viewsets
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.response import Response

from django.db.models import Prefetch, Q, Count

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import authentication
from rest_framework import exceptions
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import (
    AbstractSupplementalContent,
    AbstractCategory,
    SupplementalContent,
    AbstractLocation,
    Section,
    Subpart,
)

from .serializers import AbstractCategorySerializer, AbstractSupplementalContentSerializer, SupplementalContentSerializer


class SettingsUser:
    is_authenticated = False


class SettingsAuthentication(authentication.BasicAuthentication):
    def authenticate_credentials(self, userid, password, request=None):
        if userid == settings.HTTP_AUTH_USER and password == settings.HTTP_AUTH_PASSWORD:
            user = SettingsUser()
            user.is_authenticated = True
            return (user, None)
        raise exceptions.AuthenticationFailed('No such user')

class CategoriesViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = AbstractCategory.objects.all()
        serializer = AbstractCategorySerializer(queryset, many=True)
        return Response(serializer.data)

class SupplementalContentView(generics.ListAPIView):
    serializer_class = AbstractSupplementalContentSerializer
    arrayStrings = {'type': 'array', 'items': {'type': 'string'}}

    @extend_schema(parameters=[OpenApiParameter(name='sections', description='Sections you want to search.', required=True,
                                                type=arrayStrings),
                               OpenApiParameter(name='subparts', description='What subparts would you like to filter by.',
                                                required=False, type=arrayStrings),
                               OpenApiParameter(name='subjectgroups', description='Subject groups to filter by.',
                                                required=False, type=arrayStrings)])
    @extend_schema(description='Get a list of supplemental content')
    def get(self, *args, **kwargs):
        title = kwargs.get("title")
        part = kwargs.get("part")
        section_list = self.request.GET.getlist("sections")
        subpart_list = self.request.GET.getlist("subparts")
        subjgrp_list = self.request.GET.getlist("subjectgroups")
        start = int(self.request.GET.get("start", 0))
        maxResults = int(self.request.GET.get("max_results", 1))
        if len(section_list)==0 and len(subpart_list) ==0 and len(subjgrp_list)==0:
            query = AbstractSupplementalContent.objects.filter(
                approved=True,
                category__isnull=False,
                locations__title=title,
                locations__part=part,
            ).prefetch_related(
                Prefetch(
                    'locations',
                    queryset=AbstractLocation.objects.filter(
                        title=title,
                        part=part,
                    )
                )
            ).prefetch_related(
                Prefetch(
                    'category',
                    queryset=AbstractCategory.objects.all().select_subclasses()
                )
            ).distinct().select_subclasses(SupplementalContent).order_by(
                "-supplementalcontent__date"
                    )[start:start+maxResults]
        else:
            query = AbstractSupplementalContent.objects.filter(
                Q(locations__section__section_id__in=section_list) |
                Q(locations__subpart__subpart_id__in=subpart_list) |
                Q(locations__subjectgroup__subject_group_id__in=subjgrp_list),
                approved=True,
                category__isnull=False,
                locations__title=title,
                locations__part=part,
            ).prefetch_related(
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
            ).prefetch_related(
                Prefetch(
                    'category',
                    queryset=AbstractCategory.objects.all().select_subclasses()
                )
            ).distinct().select_subclasses(SupplementalContent).order_by(
    "-supplementalcontent__date"
)
        serializer = SupplementalContentSerializer(query, many=True)

        return Response(serializer.data)


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



class SupplementalContentByPartView(APIView):
    def get(self, request, format=None):
        part = request.GET.get('part', '')
        results = AbstractLocation.objects.filter(part=part).annotate(
            num_locations=Count(
                'supplemental_content', filter=Q(supplemental_content__approved="t")
            )).filter(
            num_locations__gt=0)
        data = {}
        for r in results:
            data[r.display_name] = r.num_locations
        return JsonResponse(data)

class SupplementalContentAll(generics.ListAPIView):
 

     
    queryset = SupplementalContent.objects.all()
    serializer_class = SupplementalContentSerializer


