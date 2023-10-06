
from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.response import Response

from common.api import OpenApiQueryParameter
from common.mixins import OptionalPaginationMixin
from file_manager.models import DocumentType, Subject
from resources.models import AbstractLocation
from resources.views.mixins import LocationExplorerViewSetMixin

from .models import ContentIndex
from .serializers import ContentSearchSerializer


@extend_schema(
    description="Search the regulation text. This endpoint is incomplete and may change. Results are paginated by default.",
    parameters=[OpenApiQueryParameter("q", "The word or phrase to search for.", str, True)] + OptionalPaginationMixin.PARAMETERS,
)
class ContentSearchViewset(viewsets.ReadOnlyModelViewSet, LocationExplorerViewSetMixin):
    serializer_class = ContentSearchSerializer
    model = ContentIndex
    @extend_schema(
        description="Retrieve list of uploaded files",
        parameters=[
                    OpenApiQueryParameter("location_details",
                                          "Specify whether to show details of a location, or just the ID.",
                                          bool, False),
                    OpenApiQueryParameter("document_type",
                                          "Limit results to only resources found within this category. Use "
                                          "\"&document_type=X\"", int, False),
                    OpenApiQueryParameter("subjects",
                                          "Limit results to only resources found within these subjects. Use "
                                          "\"&subjects=X&subjects=Y\" for multiple.", int, False),
                    OpenApiQueryParameter("q",
                                          "Search for text within file metadata. Searches document name, file name, "
                                          "date, and summary/description.", str, False),
                    ] + LocationExplorerViewSetMixin.PARAMETERS
    )
    def list(self, request):
        locations = self.request.GET.getlist("locations")
        subjects = self.request.GET.getlist("subjects")
        category = self.request.GET.getlist("category")
        search_query = self.request.GET.get("q")

        query = self.model.objects.all()

        if locations:
            q_obj = self.get_location_filter(locations)
            query = query.filter(q_obj)
        if subjects:
            query = query.filter(subject__id__in=subjects)
        if category:
            query = query.filter(category__id=category)

        locations_prefetch = AbstractLocation.objects.all().select_subclasses()
        doc_type_prefetch = DocumentType.objects.all()
        subjects_prefetch = Subject.objects.all()

        query = query.prefetch_related(
            Prefetch("locations", queryset=locations_prefetch),
            Prefetch("subject", queryset=subjects_prefetch),
            Prefetch("document_type", queryset=doc_type_prefetch)).distinct()
        if query:
            query = query.search(search_query)
        context = self.get_serializer_context()
        serializer = ContentSearchSerializer(query, many=True, context=context)
        return Response(serializer.data)
