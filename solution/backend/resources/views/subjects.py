from django.db.models import Prefetch, Q, Count, Value
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from drf_spectacular.utils import extend_schema

from resources.serializers import (
    AbstractCitationSerializer,
    PublicCategorySerializer,
    MetaCategorySerializer,
    SubpartWithChildrenSerializer,
    SectionWithParentSerializer,
    SubjectSerializer,
)

from resources.models import (
    NewSubject,
)


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubjectSerializer

    def get_queryset(self):
        return NewSubject.objects.annotate(**{
            "public_resources": Count("resources", filter=Q(resources__abstractpublicresource__isnull=False)),
            "internal_resources": (
                Count("resources", filter=Q(resources__abstractinternalresource__isnull=False))
                if self.request.user.is_authenticated else
                Value(0)
            ),
        }).order_by("combined_sort")
