from django.db.models import Count, Q, Value
from rest_framework import viewsets

from common.mixins import ViewSetPagination
from resources.models import Subject
from resources.serializers import SubjectWithCountsSerializer


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubjectWithCountsSerializer
    pagination_class = ViewSetPagination

    def get_queryset(self):
        return Subject.objects.annotate(**{
            "public_resources": Count("resources", filter=Q(resources__abstractpublicresource__isnull=False)),
            "internal_resources": (
                Count("resources", filter=Q(resources__abstractinternalresource__isnull=False))
                if self.request.user.is_authenticated else
                Value(0)
            ),
        }).order_by("combined_sort")
