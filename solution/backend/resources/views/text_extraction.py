from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.auth import SettingsAuthentication
from resources.models import AbstractResource, SingleStringModel
from resources.serializers import ContentUpdateSerializer


@extend_schema(
    description="Adds extracted text to the resource specified by the ID field.",
    request=ContentUpdateSerializer,
    responses={200: dict, 404: dict, 400: dict},
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
            if not resource.content:
                resource.content = SingleStringModel.objects.create()
                resource.save()
            resource.content.value = serializer.validated_data.get("text", "")
            resource.content.save()
            return Response(data=f"A {resource._meta.verbose_name} with ID {pk} was updated successfully.")
        except AbstractResource.DoesNotExist:
            raise NotFound(f"A resource matching {pk} does not exist.")
