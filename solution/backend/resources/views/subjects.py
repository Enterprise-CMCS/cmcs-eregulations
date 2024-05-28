from django.db.models import Count, Q, Value
from rest_framework import viewsets

from resources.models import (
    NewSubject,
)
from resources.serializers import (
    SubjectSerializer,
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
