from django.contrib import admin
from django.db.models.functions import Cast
from django.db.models import IntegerField, ManyToManyField
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.urls import path
from .mixins import ExportCsvMixin

# Register your models here.

from .models import (
    SupplementaryContent,
    Category,
    RegulationSection,
)
from .filters import (
    TitleFilter,
    PartFilter,
    SectionFilter,
)


@admin.register(RegulationSection)
class RegulationSectionAdmin(admin.ModelAdmin, ExportCsvMixin):
    change_list_template = "admin/export_all_csv.html"
    list_per_page = 500
    list_display = ("title", "part", "subpart", "section")
    search_fields = ["title", "part", "section"]
    formfield_overrides = {
        ManyToManyField: {
            "widget": FilteredSelectMultiple("Supplementary Content", is_stacked=False),
        }
    }

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('export_all_csv/', self.export_all_as_csv),

        ]
        return my_urls + urls

    actions = ["export_as_csv"]


class SectionsInline(admin.TabularInline):
    model = RegulationSection.supplementary_content.through

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "regulationsection":
            kwargs["queryset"] = RegulationSection.objects.all().annotate(
                title_int=Cast('title', IntegerField()),
                part_int=Cast('part', IntegerField()),
                section_int=Cast('section', IntegerField())
            ).order_by('title_int', 'part_int', 'section_int')
        return super(SectionsInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(SupplementaryContent)
class SupplementaryContentAdmin(admin.ModelAdmin, ExportCsvMixin):
    change_list_template = "admin/export_all_csv.html"
    list_per_page = 500
    list_display = ("date", "title", "description", "category", "created_at", "updated_at")
    search_fields = ["title", "description"]
    inlines = [
        SectionsInline,
    ]
    list_filter = (
        "approved",
        TitleFilter,
        PartFilter,
        SectionFilter,
    )

    actions = ["export_as_csv"]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('export_all_csv/', self.export_all_as_csv),

        ]
        return my_urls + urls


class ChildCategory(admin.StackedInline):
    model = Category
    fk_name = "parent"
    extra = 1
    verbose_name_plural = "Sub-Categories"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin, ExportCsvMixin):
    change_list_template = "admin/export_all_csv.html"
    list_per_page = 500
    inlines = [
        ChildCategory,
    ]
    list_display = ("title", "parent")
    actions = ["export_as_csv"]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('export_all_csv/', self.export_all_as_csv),

        ]
        return my_urls + urls
