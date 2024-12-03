from django.db.models import Count, Q, Value
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from cmcs_regulations.utils import ViewSetPagination
from resources.models import Subject
from resources.serializers import SubjectWithCountsSerializer


@extend_schema(
    tags=["resources/metadata"],
    description="Retrieve a list of subjects, each annotated with the count of associated approved public and internal "
                "resources. Authenticated users can see the count of both public and internal resources, while unauthenticated "
                "users only see the count of public resources. The subjects are ordered by a predefined sort order.",
    responses={200: SubjectWithCountsSerializer(many=True)},
)
class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubjectWithCountsSerializer
    pagination_class = ViewSetPagination

    def get_queryset(self):
        public_filter = Q(resources__abstractpublicresource__isnull=False) & Q(resources__approved=True)
        internal_filter = Q(resources__abstractinternalresource__isnull=False) & Q(resources__approved=True)
        return Subject.objects.annotate(**{
            "public_resources": Count("resources", filter=public_filter),
            "internal_resources": (
                Count("resources", filter=internal_filter)
                if self.request.user.is_authenticated else
                Value(0)
            ),
        }).order_by("combined_sort")
