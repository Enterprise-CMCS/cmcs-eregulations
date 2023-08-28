from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.response import Response

from common.api import OpenApiQueryParameter

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
