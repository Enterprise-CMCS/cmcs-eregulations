from django.apps import apps
from django.db import transaction
from django.db.models import F
from django.http import Http404, JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from common.auth import SettingsAuthentication
from parsers.models import EcfrLauncherResult, EcfrParserResult, FrParserResult, ParserConfiguration
from regcore.models import Part

from .serializers import (
    EcfrLauncherResultSerializer,
    EcfrParserResultSerializer,
    FrParserResultSerializer,
    ParserConfigurationSerializer,
    PartUploadSerializer,
)


@extend_schema(
    tags=["parsers"],
    description="Retrieve configuration for the eCFR and Federal Register parsers.",
)
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
    tags=["parsers"],
    description="Create eCFR parser result logs and retrieve most-recent eCFR parser results.",
)
class EcfrParserResultViewSet(viewsets.ModelViewSet):
    serializer_class = EcfrParserResultSerializer
    authentication_classes = [SettingsAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def _latest(self, **filters):
        parser_result = EcfrParserResult.objects.filter(**filters).order_by("-timestamp").first()
        if parser_result:
            serializer = self.get_serializer_class()(parser_result)
            return Response(serializer.data)
        raise Http404()

    def list(self, request, *args, **kwargs):
        return self._latest()

    def by_title(self, request, title):
        return self._latest(title=title)

    def by_title_part(self, request, title, part):
        return self._latest(title=title, part=part)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


@extend_schema(
    tags=["parsers"],
    description="Create eCFR launcher result logs and retrieve most-recent eCFR launcher result.",
)
class EcfrLauncherResultViewSet(viewsets.ModelViewSet):
    serializer_class = EcfrLauncherResultSerializer
    authentication_classes = [SettingsAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        launcher_result = EcfrLauncherResult.objects.order_by("-timestamp").first()
        if launcher_result:
            serializer = self.get_serializer_class()(launcher_result)
            return Response(serializer.data)
        raise Http404()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def partial_update_latest(self, request, *args, **kwargs):
        latest = EcfrLauncherResult.objects.order_by("-timestamp").first()
        if latest is None:
            raise Http404()

        serializer = self.get_serializer(latest, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @transaction.atomic
    def increment_latest_counter(self, request, *args, **kwargs):
        counter = request.data.get("counter")
        if counter not in {"succeeded_count", "failed_count"}:
            return JsonResponse({"detail": "counter must be succeeded_count or failed_count"}, status=400)

        latest = EcfrLauncherResult.objects.order_by("-timestamp").first()
        if latest is None:
            raise Http404()

        EcfrLauncherResult.objects.filter(pk=latest.pk).update(**{counter: F(counter) + 1})
        latest.refresh_from_db()
        serializer = self.get_serializer_class()(latest)
        return Response(serializer.data)


@extend_schema(
    tags=["parsers"],
    description="Create FR parser result logs and retrieve most-recent FR parser results.",
)
class FrParserResultViewSet(viewsets.ModelViewSet):
    serializer_class = FrParserResultSerializer
    authentication_classes = [SettingsAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        parser_result = FrParserResult.objects.order_by("-timestamp").first()
        if parser_result:
            serializer = self.get_serializer_class()(parser_result)
            return Response(serializer.data)
        raise Http404()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


@extend_schema(
    tags=["parsers"],
    description="Upload a regulation Part to eRegs. Typically only used by the eCFR parser.",
)
class EcfrPartUploadViewSet(viewsets.ModelViewSet):
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
        serializer = self.get_serializer(part, data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response = serializer.validated_data
        if not data.get("upload_reg_text", False):
            instance.delete()

        if apps.is_installed("content_search"):
            from content_search.utils import call_text_extractor_for_reg_text
            _, fail = call_text_extractor_for_reg_text(request, [instance])
            if fail:
                raise RuntimeError("Text extraction job could not be started.")

        return JsonResponse(response)
