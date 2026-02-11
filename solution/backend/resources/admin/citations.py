from django.contrib import admin
from django.db.models import CharField, Prefetch, Value
from django.db.models.expressions import RawSQL
from django.db.models.functions import Concat

from common.admin import CustomAdminMixin
from resources.models import (
    AbstractCitation,
    Act,
    Section,
    ActCitation,
    Subpart,
    UscCitation,
)


@admin.register(AbstractCitation)
class AbstractCitationAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ["title", "part", "child_id"]
    search_fields = ["title", "part", "child_id"]

    def get_search_results(self, request, queryset, search_term):
        search_term = search_term.lower()

        if "subpart" in search_term:
            queryset = Subpart
        elif "section" in search_term:
            queryset = Section
        else:
            queryset = AbstractCitation
        queryset = queryset.objects

        search_term = " ".join(search_term
            .replace("section", " ")
            .replace("subpart", " ")
            .replace("cfr", " ")
            .replace(".", " ")
            .split()
        )

        queryset = queryset.annotate(
            child_id_trimmed=RawSQL("LTRIM(child_id, '0')", ()),
            string=Concat("title", Value(" "), "part", Value(" "), "child_id_trimmed", output_field=CharField()),
        )

        return queryset.filter(string__icontains=search_term).select_subclasses(), True

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


@admin.register(Act)
class ActAdmin(CustomAdminMixin, admin.ModelAdmin):
    admin_priority = 9992
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(ActCitation)
class ActCitationAdmin(CustomAdminMixin, admin.ModelAdmin):
    admin_priority = 9993
    list_display = ["act", "section"]
    search_fields = ["act__name", "section"]
    ordering = ["act__name", "section"]
    fields = ["act", "section"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("act")


@admin.register(UscCitation)
class UscCitationAdmin(CustomAdminMixin, admin.ModelAdmin):
    admin_priority = 9994
    list_display = ["title", "section"]
    search_fields = ["title", "section"]
    ordering = ["title", "section"]
    fields = ["title", "section"]
