from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.response import Response

from common.api import OpenApiQueryParameter

from .functions import generate_download_link
from .models import UploadedFile
from .serializers import UploadedFileSerializer


@extend_schema(
    description="Retrieve list of uploaded files",
    parameters=[
            OpenApiQueryParameter("location_details",
                                  "Specify whether to show details of a location, or just the ID.",
                                  bool, False),]
)
class UploadedFileViewset(viewsets.ViewSet):
    serializer_class = UploadedFileSerializer
    model = UploadedFile

    def list(self, request):
        queryset = UploadedFile.objects.all()
        serializer = UploadedFileSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        queryset = UploadedFile.objects.all()
        id = kwargs.get("id")
        file = queryset.get(uid=id)
        serializer = UploadedFileSerializer(file, many=False)
        return Response(serializer.data)

    def download(self, request, *args, **kwargs):
        queryset = UploadedFile.objects.all()
        id = kwargs.get("id")
        file = queryset.get(uid=id)
        try:
            url = generate_download_link(file)
            response = HttpResponse(url, content_type='application/force-download')
            response['Content-Disposition'] = f'attachment; filename="{file.file.name}"'
            return response
        except Exception:
            print('Could not set up download url.')
            return 'Not available for download.'
