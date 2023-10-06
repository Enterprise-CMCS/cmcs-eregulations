
from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.response import Response

from common.api import OpenApiQueryParameter
from common.mixins import OptionalPaginationMixin
from file_manager.models import DocumentType, Subject
from resources.models import AbstractCategory, AbstractLocation
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
                    OpenApiQueryParameter("document-type",
                                          "Limit results to only resources found within this category. Use "
                                          "\"&document-type=X\"", int, False),
                    OpenApiQueryParameter("subjects",
                                          "Limit results to only resources found within these subjects. Use "
                                          "\"&subjects=X&subjects=Y\" for multiple.", int, False),
                    OpenApiQueryParameter("q",
                                          "Search for tsext within file metadata. Searches document name, file name, "
                                          "date, and summary/description.", str, False),
                    OpenApiQueryParameter("resource-type",
                                          "Limit results to only resources found within this resource type.  Internal, External,"
                                          "all. Use \"&resource-type=external\"", str, "all"),
                    ] + LocationExplorerViewSetMixin.PARAMETERS
    )
    def list(self, request):
        locations = self.request.GET.getlist("locations")
        subjects = self.request.GET.getlist("subjects")
        document_type = self.request.GET.getlist("document-type")
        category = self.request.GET.getlist("category")
        resource_type = self.request.GET.get("resource-type").lower()
        search_query = self.request.GET.get("q")

        query = self.model.objects.all()

        if locations:
            q_obj = self.get_location_filter(locations)
            query = query.filter(q_obj)
        if subjects:
            query = query.filter(subject__id__in=subjects)
        if category:
            query = query.filter(category__id=category)
        if document_type:
            query = query.filter(document_type__id=document_type)

        locations_prefetch = AbstractLocation.objects.all().select_subclasses()
        doc_type_prefetch = DocumentType.objects.all()
        subjects_prefetch = Subject.objects.all()
        category_prefetch = AbstractCategory.objects.all().select_subclasses().select_related("subcategory__parent")

        # If they are not authenticated they csan only get 'external' documents
        if not request.user.is_authenticated or resource_type == 'external':
            query = query.filter(resource_type='external')
        elif resource_type == 'internal':
            query = query.filter(resource_type='internal')

        query = query.prefetch_related(
            Prefetch("locations", queryset=locations_prefetch),
            Prefetch("subjects", queryset=subjects_prefetch),
            Prefetch("category", queryset=category_prefetch),
            Prefetch("document_type", queryset=doc_type_prefetch)).distinct()
        if search_query:
            query = query.search(search_query)

        context = self.get_serializer_context()
        serializer = ContentSearchSerializer(query, many=True, context=context)
        return Response(serializer.data)