from django.db.models import Count, Q, Value
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from common.mixins import ViewSetPagination
from resources.models import Subject
from resources.serializers import SubjectWithCountsSerializer


@extend_schema(
    description="Retrieve a list of subjects, each annotated with the count of associated public and internal resources. "
                "Authenticated users can see the count of both public and internal resources, while unauthenticated users "
                "only see the count of public resources. The subjects are ordered by a predefined sort order."
)
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
