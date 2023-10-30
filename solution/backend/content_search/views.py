
from django.db.models import F, Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.response import Response

from common.api import OpenApiQueryParameter
from common.mixins import PAGINATION_PARAMS, OptionalPaginationMixin
from file_manager.models import DocumentType, Subject
from resources.models import AbstractCategory, AbstractLocation
from resources.views.mixins import LocationExplorerViewSetMixin

from .models import ContentIndex
from .serializers import ContentListSerializer, ContentSearchSerializer, ContentUpdateSerializer


class ContentSearchViewset(LocationExplorerViewSetMixin, OptionalPaginationMixin, viewsets.ReadOnlyModelViewSet):
    model = ContentIndex
    queryset = ContentIndex.objects.all()
    paginate_by_default = True
    location_filter_prefix = "locations__"
    pagination_class = OptionalPaginationMixin.pagination_class

    @extend_schema(
        description="Retrieve list of uploaded files",
        parameters=[
                    OpenApiQueryParameter("category_details",
                                          "Specify whether to show details of a category, or just the ID.",
                                          bool, False),
                    OpenApiQueryParameter("location_details",
                                          "Specify whether to show details of a location, or just the ID.",
                                          bool, False),
                    OpenApiQueryParameter("document-type",
                                          "Limit results to only resources found within this category. Use "
                                          "\"&document-type=X\"", int, False),
                    OpenApiQueryParameter("subjects",
                                          "Limit results to only resources found within these subjects. Use "
                                          "\"&subjects=X&subjects=Y\" for multiple.", str, False),
                    OpenApiQueryParameter("q",
                                          "Search for text within file metadata. Searches document name, file name, "
                                          "date, and summary/description.", str, False),
                    OpenApiQueryParameter("resource-type",
                                          "Limit results to only resources found within this resource type.  Internal, External,"
                                          "all. Use \"&resource-type=external\"", str, ''),
                    ] + LocationExplorerViewSetMixin.PARAMETERS + OptionalPaginationMixin.PARAMETERS + PAGINATION_PARAMS
    )
    def list(self, request):
        locations = self.request.GET.getlist("locations")
        subjects = self.request.GET.getlist("subjects")
        document_type = self.request.GET.getlist("document-type")
        category = self.request.GET.getlist("category")
        resource_type = self.request.GET.get("resource-type")
        search_query = self.request.GET.get("q")
        paginate = self.request.GET.get("paginate") != 'false'
        query = self.queryset
        q_obj = self.get_location_filter(locations)
        if q_obj:
            query = query.filter(q_obj)
        if subjects:
            if subjects[0] == 'all':
                query = query.filter(subjects__isnull=False)
            else:
                query = query.filter(subjects__id__in=subjects)
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
        else:
            query = query.order_by(F('date_string').desc(nulls_last=True), F('doc_name_string').asc(nulls_last=True))
        if paginate:
            query = self.paginate_queryset(query)
        context = self.get_serializer_context()
        if search_query:
            serializer = ContentSearchSerializer(query, many=True, context=context)
        else:
            serializer = ContentListSerializer(query, many=True, context=context)
        if paginate:
            return self.get_paginated_response(serializer.data)
        else:
            return Response(serializer.data)


class PostContentTextViewset(viewsets.ViewSet):
    @extend_schema(
        description="Retrieve list sof uploaded files",
        request=ContentUpdateSerializer,
        responses={200: ContentUpdateSerializer}
    )
    def update(self, request, *args, **kwargs):
        post_data = request.data
        print(request.__dict__)
        id = post_data['id']
        text = post_data['text']
        index = ContentIndex.objects.get(uid=id)
        index.content = text
        index.save()
        return Response(data=f'Index was updated for {index.doc_name_string}')
