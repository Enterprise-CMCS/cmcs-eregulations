import json
import requests
import urllib.parse as urlparse
import re
from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db import transaction
from django.db.models import Case, When, F, Prefetch
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .mixins import ResourceExplorerViewSetMixin, FRDocGroupingMixin
from common.mixins import OptionalPaginationMixin, PAGINATION_PARAMS

from resources.models import (
    AbstractResource,
    SupplementalContent,
    FederalRegisterDocument,
    AbstractLocation,
    AbstractCategory,
)

from resources.serializers.resources import (
    AbstractResourcePolymorphicSerializer,
    SupplementalContentSerializer,
    FederalRegisterDocumentCreateSerializer,
    FederalRegisterDocumentSerializer,
    StringListSerializer,
    MetaResourceSerializer,
    ResourceSearchSerializer,
)

from common.auth import SettingsAuthentication


@extend_schema(
    description="Retrieve a list of all resources. "
                "Includes all types e.g. supplemental content, Federal Register Documents, etc. "
                "Searching is supported as well as inclusive filtering by title, part, subpart, and section. "
                "Results are paginated by default.",
    parameters=ResourceExplorerViewSetMixin.PARAMETERS,
    responses=MetaResourceSerializer.many(True),
)
class ResourceSearchViewSet(viewsets.ModelViewSet):
    serializer_class = ResourceSearchSerializer
    limit = 50
    gov_results = {}

    def get_annotated_url(self):
        return Case(
            When(supplementalcontent__isnull=False, then=F("supplementalcontent__url")),
            When(federalregisterdocument__isnull=False, then=F("federalregisterdocument__url")),
            default=None,
        )

    def get_gov_results(self, query, page):
        key = 'M1igE4Qcfo8LLQr7o_I9KLA6qkybmlC9IRhVCCbFbl4='
        offset = (page - 1) * self.limit
        results = []
        rstring = f'https://search.usa.gov/api/v2/search/?affiliate=reg-pilot-cms-test&access_key={key}' \
                  f'&query={query}&limit={self.limit}&offset={offset}'
        gov_results = json.loads(requests.get(rstring).text)
        if "errors" in gov_results or (gov_results["web"]["total"] == 0 and not gov_results["web"]["results"]):
            raise NotFound("Invalid page")

        for gov_result in gov_results['web']['results']:
            result = {
                'name': gov_result['title'],
                'snippet': gov_result['snippet'],
                'url': gov_result['url']
            }
            results.append(result)
        self.gov_results = {
            "total": gov_results["web"]["total"],
            "results": results,
        }

    def sort_by_url_list(self, urls, query):
        url_map = {t.url: t for t in query}
        sorted_vals = []
        for n in urls:
            sorted_vals.append(url_map[n]) if n in url_map else ''
        return sorted_vals

    def get_queryset(self, urls):

        locations_prefetch = AbstractLocation.objects.all().select_subclasses()
        category_prefetch = AbstractCategory.objects.all().select_subclasses().select_related("subcategory__parent")
        print("before query")
        query = AbstractResource.objects \
            .filter(approved=True) \
            .annotate(url_annotated=self.get_annotated_url()) \
            .filter(url_annotated__in=urls) \
            .select_subclasses().prefetch_related(
                Prefetch("locations", queryset=locations_prefetch),
                Prefetch("category", queryset=category_prefetch),
                Prefetch("related_resources", AbstractResource.objects.all().select_subclasses().prefetch_related(
                    Prefetch("locations", queryset=locations_prefetch),
                    Prefetch("category", queryset=category_prefetch),
                )),
            )

        return self.sort_by_url_list(urls, query)

    def append_snippet(self, queryset, urls):
        for q in queryset:
            q.snippet = urls[q.url]
        return queryset

    def generate_page_url(self, url, page):
        parse_url = urlparse.urlparse(url)
        url_parts = parse_url.query.split("&")
        new_url_parts = list(map(lambda x: re.sub(r"page=\d", f"page={page}", x), url_parts))
        query = "&".join(new_url_parts)
        parsed_url = parse_url._replace(query=query)
        return urlparse.urlunparse(parsed_url)

    def list(self, request, *args, **kwargs):
        q = self.request.query_params.get("q")
        page = int(self.request.query_params.get("page", 1))
        url = request.get_full_path()
        self.get_gov_results(q, page)
        urls = dict([(i['url'], i["snippet"]) for i in self.gov_results["results"]])
        queryset = self.get_queryset(urls.keys())
        resources = list(queryset)
        records = self.append_snippet(resources, urls)
        next_page = None if (page + 1) * self.limit >= self.gov_results["total"] else page + 1
        previous_page = page - 1 if page > 1 else None

        obj = {
            "count": self.gov_results["total"],
            "next": self.generate_page_url(url, next_page),
            "previous": self.generate_page_url(url, previous_page),
            "results": records,
        }

        context = self.get_serializer_context()
        context["gov_results"] = self.gov_results["results"]

        return Response(ResourceSearchSerializer(instance=obj, context=context).data)


class AbstractResourceViewSet(FRDocGroupingMixin, ResourceExplorerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = AbstractResourcePolymorphicSerializer
    model = AbstractResource

    def get_annotated_date(self):
        return Case(
            When(supplementalcontent__isnull=False, then=F("supplementalcontent__date")),
            When(federalregisterdocument__isnull=False, then=F("federalregisterdocument__date")),
            default=None,
        )

    def get_annotated_name_sort(self):
        return Case(
            When(supplementalcontent__isnull=False, then=F("supplementalcontent__name_sort")),
            When(federalregisterdocument__isnull=False, then=F("federalregisterdocument__name_sort")),
            default=None,
        )

    def get_annotated_description_sort(self):
        return Case(
            When(supplementalcontent__isnull=False, then=F("supplementalcontent__description_sort")),
            When(federalregisterdocument__isnull=False, then=F("federalregisterdocument__description_sort")),
            default=None,
        )

    def get_annotated_group(self):
        return Case(
            When(federalregisterdocument__isnull=False, then=F("federalregisterdocument__group")),
            default=-1 * F("pk"),
        )

    def get_search_fields(self):
        return {
            "supplementalcontent": ["name", "description"],
            "federalregisterdocument": ["name", "description", "document_number"],
        }


@extend_schema(
    description="Retrieve a list of all supplemental content. "
                "Searching is supported as well as inclusive filtering by title, part, subpart, and section. "
                "Results are paginated by default.",
    parameters=ResourceExplorerViewSetMixin.PARAMETERS,
)
class SupplementalContentViewSet(ResourceExplorerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = SupplementalContentSerializer
    model = SupplementalContent

    def get_search_fields(self):
        return ["name", "description"]


class FederalRegisterDocsViewSet(FRDocGroupingMixin, ResourceExplorerViewSetMixin, viewsets.ModelViewSet):
    model = FederalRegisterDocument

    authentication_classes = [SettingsAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        description="Retrieve a list of all Federal Register Documents. "
                    "Searching is supported as well as inclusive filtering by title, part, subpart, and section. "
                    "Results are paginated by default.",
        parameters=ResourceExplorerViewSetMixin.PARAMETERS,
    )
    def list(self, request, **kwargs):
        return super(FederalRegisterDocsViewSet, self).list(request, **kwargs)

    @transaction.atomic
    @extend_schema(description="Upload a Federal Register Document to the eRegs Resources system. "
                               "If the document already exists, it will be updated.")
    def update(self, request, **kwargs):
        data = request.data
        frdoc, created = FederalRegisterDocument.objects.get_or_create(document_number=data["document_number"])
        data["id"] = frdoc.pk
        sc = self.get_serializer(frdoc, data=data, context={**self.get_serializer_context(), **{"created": created}})
        try:
            if sc.is_valid(raise_exception=True):
                sc.save()
                response = sc.validated_data
                return JsonResponse(response)
        except Exception as e:
            if created:
                frdoc.delete()
            raise e

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return FederalRegisterDocumentCreateSerializer
        return FederalRegisterDocumentSerializer

    def get_search_fields(self):
        return ["name", "description", "document_number"]

    def get_annotated_group(self):
        return F("group")


@extend_schema(
    description="Retrieve a list of document numbers from all Federal Register Documents. "
                "Pagination is disabled by default.",
    parameters=OptionalPaginationMixin.PARAMETERS + PAGINATION_PARAMS,
    responses={(200, "application/json"): {"type": "string"}},
)
class FederalRegisterDocsNumberViewSet(OptionalPaginationMixin, viewsets.ReadOnlyModelViewSet):
    paginate_by_default = False
    queryset = FederalRegisterDocument.objects.all().values_list("document_number", flat=True).distinct()
    serializer_class = StringListSerializer
