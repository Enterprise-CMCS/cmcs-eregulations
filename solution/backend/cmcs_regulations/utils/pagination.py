import contextlib

from drf_spectacular.utils import OpenApiParameter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.pagination import _positive_int


# Generic pagination for viewsets.
# Provides a "page_size" parameter for controlling the number of results per page. Default page size is 100.
#
# To include additional attributes, override `get_additional_attributes` and return a dictionary of additional attributes.
# To reflect additional attributes in the OpenAPI schema, override `get_additional_attribute_schemas` and return a dictionary.
#    - See `get_paginated_response_schema` for an example of an additional attribute schema.
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

    # Overridden from DRF to get page size from query or body
    def get_page_size(self, request):
        if self.page_size_query_param:
            with contextlib.suppress(ValueError):
                return _positive_int(
                    request.GET.get(
                        self.page_size_query_param,
                        request.POST.get(
                            self.page_size_query_param,
                            self.page_size,
                        )
                    ),
                    strict=True,
                    cutoff=self.max_page_size
                )
        return self.page_size

    # Overridden from DRF to get page number from query or body
    def get_page_number(self, request, paginator):
        page_number = request.GET.get(self.page_query_param) or request.POST.get(self.page_query_param) or 1
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages
        return page_number

    def get_additional_attributes(self):
        return {}

    def get_additional_attribute_schemas(self):
        return {}

    def paginate_queryset(self, queryset, request, view=None):
        self.queryset = queryset
        self.request = request
        self.view = view
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response({
            **self.get_additional_attributes(),
            **{
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "count": self.page.paginator.count,
                "results": data,
            },
        })

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "required": ["count", "results"],
            "properties": {
                **self.get_additional_attribute_schemas(),
                "next": {
                    "type": "string",
                    "format": "uri",
                    "nullable": True,
                    "example": "http://api.example.org/accounts/?page=4",
                },
                "previous": {
                    "type": "string",
                    "format": "uri",
                    "nullable": True,
                    "example": "http://api.example.org/accounts/?page=2",
                },
                "count": {"type": "integer", "example": 123},
                "results": schema,
            },
        }
