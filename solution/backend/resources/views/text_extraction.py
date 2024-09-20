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
        pk = kwargs.get("id")
        if not pk:
            raise NotFound("The ID of the object to update must be passed in.")

        serializer = ContentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            resource = AbstractResource.objects.select_subclasses().get(pk=pk)
            content, _ = ResourceContent.objects.get_or_create(resource=resource)
            content.value = serializer.validated_data.get("text", "")
            content.save()
            return Response(data=f"A {resource._meta.verbose_name} with ID {pk} was updated successfully.")
        except AbstractResource.DoesNotExist:
            raise NotFound(f"A resource matching {pk} does not exist.")
