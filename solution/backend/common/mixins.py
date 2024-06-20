from django.core.exceptions import BadRequest
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

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

    @property
    def pagination_class(self):
        paginate = self.request.GET.get(
            "paginate",
            "true" if self.paginate_by_default else "false"
        ).lower() == "true"
        return ViewSetPagination if paginate else None


class DisplayNameFieldMixin:
    @property
    def display_name(self):
        return str(self)


def is_int(x):
    try:
        _ = int(x)
        return True
    except ValueError:
        return False


# Must define "citation_filter_prefix" (e.g. "" for none, or "citations__")
# May define "citation_filter_max_depth" to restrict to searching e.g. titles (=1), or titles and parts (=2)
class CitationFiltererMixin:
    PARAMETERS = [
        OpenApiQueryParameter("citations",
                              "Limit results to only resources linked to these CFR Citations. Use \"&citations=X&citations=Y\" "
                              "for multiple. Examples: 42, 42.433, 42.433.15, 42.433.D.", str, False),
    ]

    citation_filter_max_depth = 100

    def get_citation_filter(self, citations):
        queries = []
        for loc in citations:
            split = loc.split(".")
            length = len(split)

            if length < 1 or \
               (length >= 1 and not is_int(split[0])) or \
               (length >= 2 and (not is_int(split[0]) or not is_int(split[1]))):
                raise BadRequest(f"\"{loc}\" is not a valid title, part, section, or subpart!")

            q = Q(**{f"{self.citation_filter_prefix}title": split[0]})
            if length > 1:
                if self.citation_filter_max_depth < 2:
                    raise BadRequest(f"\"{loc}\" is too specific. You may only specify titles.")
                q &= Q(**{f"{self.citation_filter_prefix}part": split[1]})
                if length > 2:
                    if self.citation_filter_max_depth < 3:
                        raise BadRequest(f"\"{loc}\" is too specific. You may only specify titles and parts.")
                    q &= (
                        Q(**{f"{self.citation_filter_prefix}section__section_id": split[2]})
                        if is_int(split[2])
                        else (
                            Q(**{f"{self.citation_filter_prefix}subpart__subpart_id": split[2]}) |
                            Q(**{f"{self.citation_filter_prefix}section__parent__subpart__subpart_id": split[2]})
                        )
                    )

            queries.append(q)

        if queries:
            q_obj = queries[0]
            for q in queries[1:]:
                q_obj |= q
            return q_obj
        return None
