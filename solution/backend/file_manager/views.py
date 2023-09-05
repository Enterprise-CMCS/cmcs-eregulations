import requests

from django.conf import settings
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.api import OpenApiQueryParameter
from resources.models import AbstractLocation
from resources.views.mixins import LocationExplorerViewSetMixin

from .functions import establish_client
from .models import DocumentType, Subject, UploadedFile
from .serializers import DocumentTypeSerializer, SubjectSerializer, UploadedFileSerializer


@extend_schema(
    description="Retrieve a list of Upload Categories",
)
class UploadCategoryViewset(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    model = DocumentType

    def list(self, request):
        queryset = self.model.objects.all()
        serializer = DocumentTypeSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(
    description="Retrieve a list of subjects.",
)
class SubjectViewset(viewsets.ViewSet):
    model = Subject

    def list(self, request):
        queryset = self.model.objects.all()
        serializer = SubjectSerializer(queryset, many=True)
        return Response(serializer.data)


class UploadedFileViewset(viewsets.ViewSet, LocationExplorerViewSetMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = UploadedFileSerializer
    model = UploadedFile
    location_filter_prefix = "locations__"

    def get_queryset(self):
        locations = self.request.GET.getlist("locations")
        subjects = self.request.GET.getlist("subjects")
        category = self.request.GET.getlist("category")

        query = self.model.objects.all()

        q_obj = self.get_location_filter(locations)

        if q_obj:
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
        return query

    def get_serializer_context(self):
        context = {}
        context["location_details"] = self.request.GET.get("location_details", "true").lower() == "true"
        return context

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
                    ] + LocationExplorerViewSetMixin.PARAMETERS
    )
    def list(self, request):
        queryset = self.get_queryset()
        context = self.get_serializer_context()
        serializer = UploadedFileSerializer(queryset, many=True, context=context)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        queryset = UploadedFile.objects.all()
        id = kwargs.get("id")
        file = queryset.get(uid=id)
        serializer = UploadedFileSerializer(file, many=False)
        return Response(serializer.data)

    def generate_download_link(self, obj):
        s3_client = establish_client()
        try:
            print('hsersse')
            return s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                            'Key': obj.file.name},
                                                    ExpiresIn=600)

        except Exception as e:
            print(e)
            print('Could not set sup download url.')
            return 'Not avaislable for download.'

    @extend_schema(description="Download a piece of internal resource")
    def download(self, request, *args, **kwargs):
        queryset = UploadedFile.objects.all()
        id = kwargs.get("file_id")
        file = queryset.get(uid=id)
        try:
            print('his')
            url = self.generate_download_link(file)
            response = HttpResponseRedirect(url)
            response['Content-Disposition'] = f'attachment; filename="{file.file.name}"'
            return response
        except Exception:
            print('Could not set up download url.')
            return 'Not available for download.'

    def upload(self, request, *args, **kwargs):
        s3_client = establish_client()
        file_obj = None
        file_name = ''
        file = request.FILES['file']
        try:
            result = s3_client.generate_presigned_post(bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
                                                       object_name=file.name,
                                                       ExpiresIn=20)
        except:
            return
        with open(file_obj,'rb') as f:
            files = {'file': (file_obj, f)}
            http_response = requests.post(result['url'], data=result['fields'], file=file)
