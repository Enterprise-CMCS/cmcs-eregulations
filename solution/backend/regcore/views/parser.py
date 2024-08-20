from django.db import transaction
from django.http import Http404, JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from common.auth import SettingsAuthentication
from regcore.models import ECFRParserResult, ParserConfiguration, Part
from regcore.serializers.parser import (
    ParserConfigurationSerializer,
    ParserResultSerializer,
    PartUploadSerializer,
)

from .utils import OpenApiPathParameter

@extend_schema(description="Retrieve configuration for the eCFR and Federal Register parsers.")
class ParserConfigurationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ParserConfigurationSerializer

    def get_queryset(self):
        queryset = ParserConfiguration.objects.all()
        if len(queryset) < 1:
            raise Http404
        return queryset.first()

    def retrieve(self, request):
        return JsonResponse(self.get_serializer_class()(self.get_queryset()).data)


@extend_schema(
    description="Retrieve the latest ECFRParserResult or create a new ECFRParserResult object for the title.",
    parameters=[OpenApiPathParameter("title", "Title the parser was run for, e.g. 42.", int)],
)
class ParserResultViewSet(viewsets.ModelViewSet):
    serializer_class = ParserResultSerializer
    authentication_classes = [SettingsAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def retrieve(self, request, title):
        parserResult = ECFRParserResult.objects.filter(title=title).order_by("-end").first()
        if parserResult:
            serializer = self.get_serializer_class()(parserResult)
            return Response(serializer.data)
        raise Http404()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


@extend_schema(description="Upload a regulation Part to eRegs. Typically only used by the eCFR parser.")
class PartUploadViewSet(viewsets.ModelViewSet):
    serializer_class = PartUploadSerializer
    authentication_classes = [SettingsAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        data = request.data
        defaults = {
            "document": {},
            "structure": {},
            "depth_stack": [],
            "depth": -1,
        }
        part, _ = Part.objects.get_or_create(title=data["title"], name=data["name"], date=data["date"], defaults=defaults)
        data["id"] = part.pk
        sc = self.get_serializer(part, data=data)
        if sc.is_valid(raise_exception=True):
            instance = sc.save()
            response = sc.validated_data
            if not data.get("upload_reg_text", False):
                instance.delete()
            return JsonResponse(response)
