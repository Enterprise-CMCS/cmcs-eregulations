from rest_framework import viewsets
from drf_spectacular.utils import extend_schema

from common.api import OpenApiQueryParameter
from regcore.serializers.synonyms import SynonymsSerializer
from regcore.search.models import Synonym


@extend_schema(
    description="Retrieve relevant synonyms for a word or phrase",
    parameters=[OpenApiQueryParameter("synonym", "Word you are looking for a synonym for.", str, True)]
)
class SynonymViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SynonymsSerializer

    def get_queryset(self):
        syn = self.request.GET.get("q")
        return Synonym.objects.filter(baseWord__iexact=syn)
