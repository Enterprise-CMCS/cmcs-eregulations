from django.contrib import admin
from django.db.models import Prefetch

from common.admin import AbstractAdmin
from resources.models import (
    Section,
    Subpart,
)


class AbstractCitationAdmin(AbstractAdmin):
    def get_search_results(self, request, queryset, search_term):
        # TODO: use regex extract title, part, and section/subpart to search
        return super().get_search_results(request, queryset, search_term)


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
