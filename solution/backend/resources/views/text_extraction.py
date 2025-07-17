from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cmcs_regulations.utils.api_exceptions import ExceptionSerializer
from common.auth import SettingsAuthentication
from resources.models import AbstractResource, ResourceContent
from resources.serializers import ContentUpdateSerializer


@extend_schema(
    tags=["resources/metadata"],
    description="Adds extracted text to the resource specified by the ID field.",
    request=ContentUpdateSerializer,
    responses={200: str, 404: ExceptionSerializer, 400: ExceptionSerializer},
)
class ContentTextViewSet(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SettingsAuthentication]

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        serializer = ContentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        pk = kwargs.get("id", data.get("id"))
        if not pk:
            raise NotFound("The ID of the object to update must be passed in.")

        try:
            resource = AbstractResource.objects.select_subclasses().get(pk=pk)
        except AbstractResource.DoesNotExist:
            raise NotFound(f"A resource matching ID {pk} does not exist.")

        text = data.get("text")
        if text:
            content, _ = ResourceContent.objects.get_or_create(resource=resource)
            content.value = text
            content.save()

        file_type = data.get("file_type")
        if file_type:
            resource.detected_file_type = file_type

        error = data.get("error")
        if error:
            resource.extraction_error = error

        if file_type or error:
            resource.save()

        return Response(data=f"A {resource._meta.verbose_name} with ID {pk} was updated successfully.")
