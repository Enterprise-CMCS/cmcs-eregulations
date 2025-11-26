
from django.contrib import admin
from django.db.models import Prefetch, Q

from common.admin import CustomAdminMixin
from common.patterns import CITATION_REGEX
from resources.models import (
    AbstractCitation,
    Section,
    Subpart,
)


@admin.register(AbstractCitation)
class AbstractCitationAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ["title", "part", "child_id"]
    search_fields = ["title", "part", "child_id"]

    def get_search_results(self, request, queryset, search_term):
        match = CITATION_REGEX.match(search_term)
        if match:
            title = match.group(1)
            part = match.group(2)
            node_id = match.group(3)

            q = Q(**{"title" if part or node_id else "title__startswith": title})

            if part:
                q &= Q(**{"part" if node_id else "part__startswith": part})

            if node_id:
                q &= Q(section__section_id__startswith=node_id) | Q(subpart__subpart_id__startswith=node_id)

            queryset = queryset.filter(q).select_subclasses()
            return queryset, False  # False indicates no need for distinct

        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        queryset = queryset.select_subclasses()
        return queryset, use_distinct

    # Hide from the admin index and app list while keeping it registered for autocomplete
    def get_model_perms(self, request):
        return {}


@admin.register(Section)
class SectionAdmin(AbstractCitationAdmin):
    admin_priority = 9990
    list_display = ["title", "part", "section_id", "parent"]
    search_fields = ["title", "part", "section_id", "parent__subpart_id"]
    ordering = ["title", "part", "section_id", "parent"]
    fields = ["title", "part", "section_id", "parent"]
    autocomplete_fields = ["parent"]

    foreignkey_lookups = {
        "parent": lambda: Subpart.objects.all(),
    }

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            Prefetch("parent", Subpart.objects.all()),
        )


@admin.register(Subpart)
class SubpartAdmin(AbstractCitationAdmin):
    admin_priority = 9991
    list_display = ["title", "part", "subpart_id"]
    search_fields = ["title", "part", "subpart_id"]
    ordering = ["title", "part", "subpart_id"]
    fields = ["title", "part", "subpart_id"]
