from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator
from .api import OpenApiQueryParameter


# For viewsets where pagination is disabled by default
PAGINATION_PARAMS = [
    OpenApiQueryParameter("page", "A page number within the paginated result set.", int, False),
    OpenApiQueryParameter("page_size", "Number of results to return per page.", int, False),
]


class ViewSetPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 1000
    page_size = 100


# May define "paginate_by_default = False" to disable pagination unless explicitly requested
# Pagination can be enabled/disabled with "?paginate=true/false"
class OptionalPaginationMixin:
    PARAMETERS = [
        OpenApiQueryParameter("paginate", "Enable or disable pagination. If enabled, results will be wrapped in a JSON object. "
                              "If disabled, a normal JSON array will be returned.", bool, False),
    ]

    paginate_by_default = True

    def pagination_details(self, results, query):
        page = self.request.GET.get('page', 1)
        page_size = self.request.GET.get('page_size', 100)

        paginator = Paginator(results, page_size)
        last_page = int(paginator.num_pages)
        valid_url = self.request.build_absolute_uri(f"/v3/search?page={last_page}&page_size={page_size}&q={query}")
        valid = last_page >= int(page)
        context = {
            "valid": valid,
            "count": int(paginator.count),
            "detail": "Valid page." if valid else "Invalid page.",
            "last_available_page": int(paginator.num_pages),
            "last_page_url": valid_url}
        return context

    @property
    def pagination_class(self):
        paginate = self.request.GET.get(
            "paginate",
            "true" if self.paginate_by_default else "false"
        ).lower() == "true"
        return ViewSetPagination if paginate else None
