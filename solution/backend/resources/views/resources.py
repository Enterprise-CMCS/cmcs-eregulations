import json
import os
import re
import requests

from itertools import chain

import urllib.parse as urlparse
from drf_spectacular.utils import extend_schema
from django.db import transaction
from django.db.models import Case, When, F, Prefetch, Q
from django.http import JsonResponse
from requests.exceptions import ConnectTimeout
from rest_framework import viewsets
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .mixins import (
    ResourceExplorerViewSetMixin,
    FRDocGroupingMixin
)
from common.mixins import (
    OptionalPaginationMixin,
    PAGINATION_PARAMS
)
from common.auth import SettingsAuthentication

from resources.models import (
    AbstractCategory,
    AbstractLocation,
    AbstractResource,
    FederalRegisterDocument,
    SupplementalContent,
)

from resources.serializers.resources import (
    AbstractResourcePolymorphicSerializer,
    FederalRegisterDocumentCreateSerializer,
    FederalRegisterDocumentSerializer,
    MetaResourceSerializer,
    ResourceSearchSerializer,
    StringListSerializer,
    SupplementalContentSerializer,
)


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

    def format_gov_results(self, gov_results):
        if gov_results["web"]["total"] == 0:
            raise NotFound("No results from search.gov")
        elif not gov_results["web"]["results"]:
            raise NotFound("Search.gov out of bounds")
        results = []

        for gov_result in gov_results['web']['results']:
            results.append({
                'name': gov_result['title'],
                'snippet': gov_result['snippet'],
                'url': gov_result['url']})
        self.gov_results = {
            "total": gov_results["web"]["total"],
            "results": results,
        }

    def get_gov_results(self, query, page):
        key = os.environ.get('SEARCHGOV_KEY')
        site_name = os.environ.get('SEARCHGOV_SITE_NAME')

        offset = (page - 1) * self.limit

        rstring = f'https://search.usa.gov/api/v2/search/?affiliate={site_name}&access_key={key}' \
                  f'&query={urlparse.quote_plus(query)}&limit={self.limit}&offset={offset}'
        try:
            gov_results = json.loads(requests.get(rstring, timeout=3).text)
        except ConnectTimeout:
            raise NotFound("Errors.  Search.gov took to long to return a response.")
        except ValueError:
            raise ParseError("Error retrieving proper data from search.gov")
        self.format_gov_results(gov_results)

    # Search.gov does not have the full urls so we need to split at the # for the index
    def sort_by_url_list(self, urls, resources):
        res_index = {}
        for r in resources:
            if r.url.split("#")[0] in res_index:
                res_index[r.url.split("#")[0]].append(r)
            else:
                res_index[r.url.split("#")[0]] = [r]
        sorted_vals = []
        for url in urls:
            sorted_vals.append(res_index[url]) if url in res_index else None
        return sorted_vals

    def get_queryset(self, urls):

        locations_prefetch = AbstractLocation.objects.all().select_subclasses()
        category_prefetch = AbstractCategory.objects.all().select_subclasses().select_related("subcategory__parent")

        url_filters = [Q(url_annotated__istartswith=url) for url in urls]
        # gets thes first of the list to being the query set
        url_query = url_filters.pop()

        # now we are combining the remaing ones by putting an or statement in between.
        # So now its like url_annotate_starts with url 1 or url annotated starts with url2 etc.
        for url in url_filters:
            url_query |= url
        query = AbstractResource.objects \
            .filter(approved=True) \
            .annotate(url_annotated=self.get_annotated_url()) \
            .filter(url_query) \
            .select_subclasses().prefetch_related(
                Prefetch("locations", queryset=locations_prefetch),
                Prefetch("category", queryset=category_prefetch),
                Prefetch("related_resources", AbstractResource.objects.filter(approved=True).select_subclasses().prefetch_related(
                    Prefetch("locations", queryset=locations_prefetch),
                    Prefetch("category", queryset=category_prefetch),
                )),
            )

        return self.sort_by_url_list(urls, query)

    def append_snippet(self, queryset, urls):
        for resource in queryset:
            resource.snippet = urls[resource.url.split("#")[0]]
        return queryset

    def generate_page_url(self, url, page):
        if not page:
            return None
        parse_url = urlparse.urlparse(url)
        url_parts = parse_url.query.split("&")
        new_url_parts = list(map(lambda x: re.sub(r"page=\d", f"page={page}", x), url_parts))
        query = "&".join(new_url_parts)
        parsed_url = parse_url._replace(query=query)
        return urlparse.urlunparse(parsed_url)

    def result_object(self, url, records, page):
        next_page = None if page * self.limit >= self.gov_results["total"] else page + 1
        previous_page = page - 1 if page > 1 else None
        obj = {
            "count": self.gov_results["total"],
            "next": self.generate_page_url(url, next_page),
            "previous": self.generate_page_url(url, previous_page),
            "results": records,
        }
        return obj

    def list(self, request, *args, **kwargs):
        q = self.request.query_params.get("q")
        page = int(self.request.query_params.get("page", 1))
        url = request.get_full_path()
        self.get_gov_results(q, page)
        urls = dict([(i['url'], i["snippet"]) for i in self.gov_results["results"]])
        queryset = self.get_queryset(urls.keys())
        resources = list(chain.from_iterable(queryset))
        records = self.append_snippet(resources, urls)

        obj = self.result_object(url, records, page)

        context = self.get_serializer_context()

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
