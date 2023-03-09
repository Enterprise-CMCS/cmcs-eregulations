from django.db.models import Q, F, Prefetch, OuterRef, Subquery
from django.contrib.postgres.search import SearchHeadline, SearchQuery, SearchVector, SearchRank
from django.core.exceptions import BadRequest

from common.api import OpenApiQueryParameter
from resources.models import (
    AbstractLocation,
    AbstractResource,
    AbstractCategory,
    FederalRegisterDocument,
    FederalRegisterDocumentGroup
)

from common.mixins import OptionalPaginationMixin


def is_int(x):
    try:
        _ = int(x)
        return True
    except ValueError:
        return False


# Must define "location_filter_prefix" (e.g. "" for none, or "locations__")
# May define "location_filter_max_depth" to restrict to searching e.g. titles (=1), or titles and parts (=2)
class LocationFiltererMixin:
    PARAMETERS = [
        OpenApiQueryParameter("locations",
                              "Limit results to only resources linked to these locations. Use \"&locations=X&locations=Y\" "
                              "for multiple. Examples: 42, 42.433, 42.433.15, 42.433.D.", str, False),
    ]

    location_filter_max_depth = 100

    def get_location_filter(self, locations):
        queries = []
        for loc in locations:
            split = loc.split(".")
            length = len(split)

            if length < 1 or \
               (length >= 1 and not is_int(split[0])) or \
               (length >= 2 and (not is_int(split[0]) or not is_int(split[1]))):
                raise BadRequest(f"\"{loc}\" is not a valid title, part, section, or subpart!")

            q = Q(**{f"{self.location_filter_prefix}title": split[0]})
            if length > 1:
                if self.location_filter_max_depth < 2:
                    raise BadRequest(f"\"{loc}\" is too specific. You may only specify titles.")
                q &= Q(**{f"{self.location_filter_prefix}part": split[1]})
                if length > 2:
                    if self.location_filter_max_depth < 3:
                        raise BadRequest(f"\"{loc}\" is too specific. You may only specify titles and parts.")
                    q &= (
                        Q(**{f"{self.location_filter_prefix}section__section_id": split[2]})
                        if is_int(split[2])
                        else Q(**{f"{self.location_filter_prefix}subpart__subpart_id": split[2]})
                    )

            queries.append(q)

        if queries:
            q_obj = queries[0]
            for q in queries[1:]:
                q_obj |= q
            return q_obj
        return None


# Provides a filterable location viewset
class LocationExplorerViewSetMixin(OptionalPaginationMixin, LocationFiltererMixin):
    PARAMETERS = LocationFiltererMixin.PARAMETERS + OptionalPaginationMixin.PARAMETERS

    location_filter_prefix = ""
    location_filter_max_depth = 2

    def get_queryset(self):
        query = super().get_queryset()

        locations = self.request.GET.getlist("locations")
        q_obj = self.get_location_filter(locations)
        if q_obj:
            query = query.filter(q_obj)

        return query.distinct()


# In order for the order of fed reg documents to be in the correct order, the latest document needs to be extracted.
# IF a search is done by location and fr_grouping is there results could appear out of order if the most recent document
# is not associated to the location it makes the results look weird.  This fixes it.
# TODO: Make this mixin handle everything about the "fr_grouping" parameter too, not passed in as a method parameter.
class FRDocGroupingMixin:
    PARAMETERS = [
        OpenApiQueryParameter("fr_grouping", "Determines if FR Documents should be grouped or not"
                              "Default is true", bool, False),
    ]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["fr_grouping"] = self.request.GET.get("fr_grouping", "true").lower() == "true"
        return context

    def get_final_ids(self, id_query):
        fr_grouping = self.request.GET.get("fr_grouping", "true").lower() == "true"
        if fr_grouping:
            fr_groups = []
            ids = []

            for i in id_query:
                if i.group_annotated not in fr_groups:
                    fr_groups.append(i.group_annotated)
                # Supplemental content either is none or negative on group annotated. Those must be on the list if requested for
                # abstract resource
                if i.group_annotated is None or i.group_annotated < 0:
                    ids.append(i.id)

            #  This uses a subquery  to get the latest fr_document ID for the fr groups and uses that in place of the original
            #  ID found.
            if fr_groups:
                newest = FederalRegisterDocument.objects.filter(group_id=OuterRef('pk')).order_by('-date')
                groups = FederalRegisterDocumentGroup.objects\
                    .annotate(newest_doc=Subquery(newest.values('id')[:1]))\
                    .filter(id__in=fr_groups)\
                    .values_list('newest_doc', flat=True)
                ids = list(groups) + ids
        else:
            ids = super().get_final_ids(id_query)
        return ids


# Provides a filterable and searchable viewset for any type of resource
# Must implement get_search_fields() as a list of fields or a map of model names to lists of fields
# Must provide "model" as the resource model type to display
# May override get_annotated_date() for complex date lookups
# May override get_annotated_group() to limit particular model types to one result per group
#     (By default, -1*pk is used so that no resource gets removed)
class ResourceExplorerViewSetMixin(OptionalPaginationMixin, LocationFiltererMixin):
    PARAMETERS = [
        OpenApiQueryParameter("category_details", "Specify whether to show details of a category, or just the ID.", bool, False),
        OpenApiQueryParameter("location_details", "Specify whether to show details of a location, or just the ID.", bool, False),
        OpenApiQueryParameter("q", "Search query for resources. Supports literal phrase matching by surrounding the "
                              "search with quotes.", str, False),
        OpenApiQueryParameter("categories", "Limit results to only resources found within these categories. Use "
                              "\"&categories=X&categories=Y\" for multiple.", int, False),
        OpenApiQueryParameter("sort", "Sort results by this field. Valid values are \"newest\", \"oldest\", and \"relevance\". "
                              "Newest is the default, and relevance requires a search query.", str, False),
    ] + OptionalPaginationMixin.PARAMETERS + LocationFiltererMixin.PARAMETERS

    location_filter_prefix = "locations__"

    def get_search_fields(self):
        raise NotImplementedError

    def get_annotated_date(self):
        return F("date")

    def get_annotated_name_sort(self):
        return F("name_sort")

    def get_annotated_description_sort(self):
        return F("description_sort")

    def get_annotated_group(self):
        return -1*F("pk")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["category_details"] = self.request.GET.get("category_details", "true").lower() == "true"
        context["location_details"] = self.request.GET.get("location_details", "true").lower() == "true"
        return context

    def get_search_vectors(self):
        v = None
        search_fields = self.get_search_fields()
        if isinstance(search_fields, type([])):
            for field in search_fields:
                vector = SearchVector(field, weight="A", config="english")
                v = v + vector if v else vector
        else:
            for model in search_fields:
                for field in search_fields[model]:
                    vector = SearchVector(f"{model}__{field}", weight="A", config="english")
                    v = v + vector if v else vector
        return v

    def make_headline(self, field, search_query, search_type):
        return SearchHeadline(
            field,
            SearchQuery(search_query, search_type=search_type, config="english"),
            start_sel='<span class="search-headline">',
            stop_sel='</span>',
            config="english",
            highlight_all=True,
        )

    def get_search_headlines(self, search_query, search_type):
        annotations = {}
        search_fields = self.get_search_fields()
        if isinstance(search_fields, type([])):
            for field in search_fields:
                annotations[f"{field}_headline"] = self.make_headline(field, search_query, search_type)
        else:
            for model in search_fields:
                for field in search_fields[model]:
                    annotations[f"{model}_{field}_headline"] = self.make_headline(f"{model}__{field}", search_query, search_type)
        return annotations

    def get_final_ids(self, id_query):
        return [i[0] for i in id_query.values_list("id", "group_annotated")]

    def get_queryset(self):
        locations = self.request.GET.getlist("locations")
        categories = self.request.GET.getlist("categories")
        search_query = self.request.GET.get("q")
        sort_method = self.request.GET.get("sort")

        id_query = self.model.objects\
                       .filter(approved=True)\
                       .annotate(group_annotated=self.get_annotated_group())

        q_obj = self.get_location_filter(locations)
        if q_obj:
            id_query = id_query.filter(q_obj)

        if categories:
            id_query = id_query.filter(category__id__in=categories)

        ids = self.get_final_ids(id_query)

        annotations = {}
        locations_prefetch = AbstractLocation.objects.all().select_subclasses()
        category_prefetch = AbstractCategory.objects.all().select_subclasses().select_related("subcategory__parent")\
                                            .contains_fr_docs()
        query = self.model.objects.filter(id__in=ids).select_subclasses().prefetch_related(
            Prefetch("locations", queryset=locations_prefetch),
            Prefetch("category", queryset=category_prefetch),
            Prefetch("related_resources", AbstractResource.objects.all().select_subclasses().prefetch_related(
                Prefetch("locations", queryset=locations_prefetch),
                Prefetch("category", queryset=category_prefetch),
            )),
        )

        if search_query:
            (search_type, cover_density) = (
                ("phrase", True)
                if search_query.startswith('"') and search_query.endswith('"')
                else ("plain", False)
            )
            annotations["rank"] = SearchRank(
                self.get_search_vectors(),
                SearchQuery(search_query, search_type=search_type, config="english"),
                cover_density=cover_density,
            )
            annotations = {**annotations, **self.get_search_headlines(search_query, search_type)}

        annotations["date_annotated"] = self.get_annotated_date()
        annotations["annotated_name_sort"] = self.get_annotated_name_sort()
        annotations["annotated_description_sort"] = self.get_annotated_description_sort()

        query = query.annotate(**annotations)
        query = query.filter(rank__gte=0.2) if search_query else query

        if search_query and sort_method == "relevance":
            return query.distinct().order_by("-rank")
        elif sort_method == "oldest":
            return query.distinct().order_by(F("date_annotated").asc(nulls_last=True),
                                             F("annotated_name_sort").asc(nulls_last=True),
                                             F("annotated_description_sort").asc(nulls_last=True))
        else:
            return query.order_by(F("date_annotated").desc(nulls_last=True),
                                  F("annotated_name_sort").asc(nulls_last=True),
                                  F("annotated_description_sort").asc(nulls_last=True)).distinct()
        return query.order_by(F("date_annotated").desc(nulls_last=True)).distinct()
