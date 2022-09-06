from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.http import Http404
from drf_spectacular.utils import extend_schema

from .utils import OpenApiPathParameter
from regcore.serializers import ParserResultSerializer
from regcore.views import SettingsAuthentication
from regcore.models import ECFRParserResult


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
            serializer = self.serializer_class(parserResult)
            return Response(serializer.data)
        raise Http404()
