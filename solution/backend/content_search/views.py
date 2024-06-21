import json

import requests
from django.conf import settings
from django.core.exceptions import BadRequest
from django.db.models import Prefetch, Q
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.auth import SettingsAuthentication
from common.functions import establish_client
from common.mixins import CitationFiltererMixin, ViewSetPagination
from resources.models import (
    AbstractCategory,
    AbstractCitation,
    AbstractResource,
    Subject,
)

from .models import ContentIndex
from .serializers import ContentSearchSerializer, ContentUpdateSerializer


@extend_schema(
    description="Retrieve list of uploaded files",
    parameters=[
        OpenApiParameter(
            name="subjects",
            required=False,
            type=int,
            description="Limit results to only resources found within these subjects. Subjects are referenced by ID, not name. "
                        "Use \"&subjects=1&subjects=2\" for multiple.",
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="categories",
            required=False,
            type=int,
            description="Limit results to only resources found within these categories. Categories are referenced by ID, not "
                        "name. Use \"&categories=1&categories=2\" for multiple.",
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="q",
            required=True,
            type=str,
            description="Search for this text within public and internal resources, and regulation text. "
                        "Fields searched depends on the underlying data type.",
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="show_public",
            required=False,
            type=str,
            description="Show ('true') or hide ('false') public resources, including Federal Register and other public links. "
                        "Default is true.",
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="show_internal",
            required=False,
            type=str,
            description="Show ('true') or hide ('false') internal resources, including files and internal links. "
                        "Default is true.",
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="show_regulations",
            required=False,
            type=str,
            description="Show ('true') or hide ('false') regulation text, including sections and appendices. "
                        "Default is true.",
            location=OpenApiParameter.QUERY,
        ),
    ]  # + LocationFiltererMixin.PARAMETERS + PAGINATION_PARAMS
)
class ContentSearchViewSet(CitationFiltererMixin, viewsets.ReadOnlyModelViewSet):
    model = ContentIndex
    serializer_class = ContentSearchSerializer
    citation_filter_prefix = "resource__cfr_citations__"
    pagination_class = ViewSetPagination

    def get_boolean_parameter(self, param, default):
        value = self.request.GET.get(param)
        if not value:
            return default
        value = value.lower().strip()
        if value in ("true", "t", "y", "yes", "1"):
            return True
        elif value in ("false", "f", "n", "no", "0"):
            return False
        raise BadRequest(f"Parameter '{param}' has an invalid value: '{value}'.")

    def get_queryset(self):
        citations = self.request.GET.getlist("citations")
        subjects = self.request.GET.getlist("subjects")
        categories = self.request.GET.getlist("categories")
        show_public = self.get_boolean_parameter("show_public", True)
        show_internal = self.get_boolean_parameter("show_internal", True)
        show_regulations = self.get_boolean_parameter("show_regulations", True)

        # Retrieve the required search query param
        search_query = self.request.GET.get("q")
        if not search_query:
            raise BadRequest("A search query is required; provide 'q' parameter in the query string.")

        query = ContentIndex.objects.all()

        # Filter inclusively by citations if this array exists
        citation_filter = self.get_citation_filter(citations)
        if citation_filter:
            query = query.filter(citation_filter)

        # Filter by subject pks if subjects array is present
        if subjects:
            query = query.filter(resource__subjects__pk__in=subjects)

        # Filter by categories (both parent and subcategories) if the categories array is present
        if categories:
            query = query.filter(
                Q(resource__category__pk__in=categories) |
                Q(resource__category__abstractpubliccategory__publicsubcategory__parent__pk__in=categories) |
                Q(resource__category__abstractinternalcategory__internalsubcategory__parent__pk__in=categories)
            )

        # Filter by public, internal, and regulation text
        if not show_public:
            query = query.exclude(resource__abstractpublicresource__isnull=False)
        if not show_internal or not self.request.user.is_authenticated:
            query = query.exclude(resource__abstractinternalresource__isnull=False)
        if not show_regulations:
            query = query.exclude(reg_text__isnull=False)

        # Perform search and headline generation
        query = query.search(search_query)
        ranked_results = [i.pk for i in self.paginate_queryset(query)]
        query = ContentIndex.objects.filter(pk__in=ranked_results).generate_headlines(search_query)

        # Prefetch all related data
        query = query.prefetch_related(
            Prefetch("resource", AbstractResource.objects.select_subclasses().prefetch_related(
                Prefetch("cfr_citations", AbstractCitation.objects.select_subclasses()),
                Prefetch("category", AbstractCategory.objects.select_subclasses()),
                Prefetch("subjects", Subject.objects.all()),
            )),
        )

        return query


@extend_schema(
    description="Adds text to the content of an index.",
    request=ContentUpdateSerializer,
    responses={200: ContentUpdateSerializer}
)
class PostContentTextViewset(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SettingsAuthentication]

    def post(self, request, *args, **kwargs):
        post_data = request.data
        id = post_data['id']
        text = post_data['text']
        try:
            rows = ContentIndex.objects.filter(id=id).update(content=text)
            return Response(data=f"Index was updated for {rows} rows.")
        except ContentIndex.DoesNotExist:
            raise BadRequest(f"An index matching {id} does not exist.")


@extend_schema(
    description="Invokes the text extractor for the given content index ID.",
)
class InvokeTextExtractorViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response("Not implemented")
