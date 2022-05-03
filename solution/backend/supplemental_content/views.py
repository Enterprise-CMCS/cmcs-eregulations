from django.http import JsonResponse

from rest_framework import generics, viewsets
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.response import Response

from django.db.models import Prefetch, Q, Count
from django.contrib.postgres.search import SearchHeadline, SearchQuery, SearchVector, SearchRank

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import authentication
from rest_framework import exceptions
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from .models import (
    AbstractSupplementalContent,
    AbstractCategory,
    TempSupplementalContent,
    AbstractLocation,
    Section,
    Subpart,
)

from .serializers import (
    AbstractCategorySerializer,
    AbstractSupplementalContentSerializer,
    SupplementalContentSerializer,
    IndividualSupSerializer,
    SuppByLocationSerializer
)


class SettingsUser:
    is_authenticated = False


class SettingsAuthentication(authentication.BasicAuthentication):
    def authenticate_credentials(self, userid, password, request=None):
        if userid == settings.HTTP_AUTH_USER and password == settings.HTTP_AUTH_PASSWORD:
            user = SettingsUser()
            user.is_authenticated = True
            return (user, None)
        raise exceptions.AuthenticationFailed('No such user')


class CategoriesViewSet(viewsets.ModelViewSet):
    serializer_class = AbstractCategorySerializer
    queryset = AbstractCategory.objects.all()


class SupplementalContentView(generics.ListAPIView):
    serializer_class = AbstractSupplementalContentSerializer
    arrayStrings = {'type': 'array', 'items': {'type': 'string'}}

    @extend_schema(parameters=[OpenApiParameter(name='sections', description='Sections you want to search.', required=True,
                                                type=arrayStrings),
                               OpenApiParameter(name='subparts', description='What subparts would you like to filter by.',
                                                required=False, type=arrayStrings)])
    @extend_schema(description='Get a list of supplemental content')
    def get(self, *args, **kwargs):
        title = kwargs.get("title")
        part = kwargs.get("part")
        section_list = self.request.GET.getlist("sections")
        subpart_list = self.request.GET.getlist("subparts")
        start = int(self.request.GET.get("start", 0))
        maxResults = int(self.request.GET.get("max_results", 1000))

        q = self.request.query_params.get('q')

        query = AbstractSupplementalContent.objects

        if len(section_list) > 0 or len(subpart_list) > 0 or len(subjgrp_list) > 0:
            query = query.filter(
                Q(locations__section__section_id__in=section_list) |
                Q(locations__subpart__subpart_id__in=subpart_list),
            )

        query = query.filter(
            approved=True,
            category__isnull=False,
        )

        if title != "all":
            query = query.filter(locations__title=title)

        if part != "all":
            query = query.filter(locations__part=part)

        if q:
            search_type = 'plain'
            cover_density = False

            if (q.startswith('"')) and q.endswith('"'):
                search_type = 'phrase'
                cover_density = True

            query = query.annotate(rank=SearchRank(
                    SearchVector('supplementalcontent__name', weight='A', config='english')
                    + SearchVector('supplementalcontent__description', weight='A', config='english'),
                    SearchQuery(q, search_type=search_type, config='english'), cover_density=cover_density))

            query = query.filter(rank__gte=0.2).annotate(
                nameHeadline=SearchHeadline(
                    "supplementalcontent__name",
                    SearchQuery(q, search_type=search_type, config='english'),
                    start_sel='<span class="search-highlight">',
                    stop_sel='</span>',
                    config='english'
                ),
                descriptionHeadline=SearchHeadline(
                    "supplementalcontent__description",
                    SearchQuery(q, search_type=search_type, config='english'),
                    start_sel='<span class="search-highlight">',
                    stop_sel='</span>',
                    config='english',
                    highlight_all=True
                )
            )

        query = query.prefetch_related(
                    Prefetch(
                        'locations',
                        queryset=AbstractLocation.objects.all()
                    )
                ).prefetch_related(
                    Prefetch(
                        'category',
                        queryset=AbstractCategory.objects.all().select_subclasses()
                    )
                ).distinct().select_subclasses(SupplementalContent).order_by(
                    "-rank" if q else "-supplementalcontent__date"
                )[start:start+maxResults]
        serializer = SupplementalContentSerializer(query, many=True)

        return Response(serializer.data)


@extend_schema(
        parameters=[
          OpenApiParameter("start", int, OpenApiParameter.QUERY),
          OpenApiParameter("max_results", int, OpenApiParameter.QUERY)
        ],
    )
class AllSupplementalContentView(APIView):
    def get(self, *args, **kwargs):
        start = int(self.request.GET.get("start", 0))
        maxResults = int(self.request.GET.get("max_results", 1000))
        categories = self.request.GET.getlist("category")

        query = AbstractSupplementalContent.objects.filter(
                approved=True,
                category__isnull=False
            )

        if len(categories) > 0:
            query = query.filter(category__id__in=categories).prefetch_related(
                Prefetch(
                    'category',
                    queryset=AbstractCategory.objects.filter(category__id__in=categories).select_subclasses()
                )
            )
        else:
            query = query.prefetch_related(
                    Prefetch(
                        'category',
                        queryset=AbstractCategory.objects.all().select_subclasses()
                    )
                )

        query = query.prefetch_related(
                Prefetch(
                    'locations',
                    queryset=AbstractLocation.objects.all()
                )
            ).distinct().select_subclasses(TempSupplementalContent).order_by(
                "-supplementalcontent__date"
            )[start:start+maxResults]
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
    @extend_schema(
        parameters=[
            OpenApiParameter("part", str, OpenApiParameter.QUERY), ],
        responses={
            (200, 'application/json'): OpenApiTypes.OBJECT}
    )
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


class SupByLocationViewSet(viewsets.ModelViewSet):

    def list(self, request, *args, **kwargs):
        queryset = AbstractLocation.objects.prefetch_related(
                    Prefetch(
                        'supplemental_content',
                        queryset=AbstractSupplementalContent.objects.filter(approved=True).select_subclasses(TempSupplementalContent)
                    ))
        serializer = SuppByLocationSerializer(queryset, many=True)
        response_dict = {}
        for item in serializer.data:
            titleKey = item.pop("title")
            partKey = item.pop("part")
            is_subpart = False
            if 'Subpart' in item['display_name']:
                identifier = item['display_name'][-1]
                is_subpart = True
            else:
                identifier = item['display_name'].split()[1].split('.')

            newsup = []
            for content in item['supplemental_content']:
                newsup.append(content['id'])

            if len(identifier) > 1 or is_subpart:
                if is_subpart:
                    location = {identifier: newsup}
                else:
                    identifier = identifier[1]
                    location = {identifier: newsup}
                partDict = {partKey: location}
                if titleKey in response_dict:
                    if partKey in response_dict[titleKey]:
                        response_dict[titleKey][partKey][identifier] = newsup
                    else:
                        response_dict[titleKey][partKey] = location
                else:
                    response_dict = {titleKey: partDict}

        return Response(response_dict)


class SupByIdViewSet(viewsets.ViewSet):

    def list(self, request, *args, **kwargs):
        title = kwargs.get("title")
        part = kwargs.get("part")
        queryset = AbstractSupplementalContent.objects.filter(
            approved=True,
            category__isnull=False,
            locations__part=part,
            locations__title=title
        ).prefetch_related(
                    Prefetch(
                        'locations',
                        queryset=AbstractLocation.objects.all()
                    )
                ).prefetch_related(
                    Prefetch(
                        'category',
                        queryset=AbstractCategory.objects.all().select_subclasses()
                    )
                ).distinct().select_subclasses(TempSupplementalContent).order_by(
                    "-supplementalcontent__date"
                )
        serializer = IndividualSupSerializer(queryset, many=True)
        response_dict = {}

        for item in serializer.data:
            idKey = item.pop('id')
            response_dict[idKey] = item

        return Response(response_dict)
