from django.db.models import Count
from drf_spectacular.utils import OpenApiParameter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


# Generic pagination for viewsets.
# Provides a "page_size" parameter for controlling the number of results per page. Default page size is 100.
#
# To include counts of types in the response, subclass this and override `get_count_map` to return a list
# of dictionaries of the form: {"name": "name_of_count", "count_field": "field_to_count", "filter": Q() filter or None}.
#
# To include additional attributes, override `get_additional_attributes` and return a dictionary of additional attributes.
class ViewSetPagination(PageNumberPagination):
    QUERY_PARAMETERS = [
        OpenApiParameter(
            name="page",
            description="A page number within the paginated result set.",
            required=False,
            type=int,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="page_size",
            description="Number of results to return per page. Default is 100. "
                        "Avoid high numbers to prevent slowdowns and timeouts.",
            required=False,
            type=int,
            location=OpenApiParameter.QUERY,
        ),
    ]

    page_size_query_param = "page_size"
    max_page_size = 1000
    page_size = 100

    def get_count_map(self):
        return None

    def get_additional_counts(self):
        additional_counts = self.get_count_map()
        if not additional_counts:
            return {}
        counts = self.queryset.aggregate(
            **{count["name"]: Count(count["count_field"], filter=count["filter"]) for count in additional_counts}
        )
        return {count["name"]: counts[count["name"]] for count in additional_counts}

    def get_additional_attributes(self):
        return {}

    def paginate_queryset(self, queryset, request, view=None):
        self.queryset = queryset
        self.request = request
        self.view = view
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response({
            **self.get_additional_attributes(),
            **self.get_additional_counts(),
            **{
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "count": self.page.paginator.count,
                "results": data,
            },
        })
