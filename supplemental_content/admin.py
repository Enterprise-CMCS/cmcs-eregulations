from django.contrib import admin
from django.contrib.admin.sites import site
from django.apps import apps
from django.urls import path
from django.db.models import Q

# Register your models here.

from .models import (
    SupplementalContent,
    Category,
    SubCategory,
    SubSubCategory,
    AbstractLocation,
    Section,
    SubjectGroup,
    Subpart,
)

from .filters import (
    TitleFilter,
    PartFilter,
    SectionFilter,
    SubpartFilter,
    SubjectGroupFilter,
)

from .mixins import ExportCsvMixin
from . import actions


class BaseAdmin(admin.ModelAdmin, ExportCsvMixin):
    change_list_template = "admin/export_all_csv.html"
    list_per_page = 500
    admin_priority = 20
    actions = ["export_as_csv"]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('export_all_csv/', self.export_all_as_csv),
            path('export_all_json/', self.export_all_as_json),
        ]
        return my_urls + urls


@admin.register(Section)
class SectionAdmin(BaseAdmin):
    admin_priority = 40
    list_display = ("title", "part", "section_id", "parent")
    search_fields = ["title", "part", "section_id"]
    ordering = ("title", "part", "section_id", "parent")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs["queryset"] = AbstractLocation.objects.filter(Q(subpart__isnull=False) | Q(subjectgroup__isnull=False))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Subpart)
class SubpartAdmin(BaseAdmin):
    admin_priority = 50
    list_display = ("title", "part", "subpart_id")
    search_fields = ["title", "part", "subpart_id"]
    ordering = ("title", "part", "subpart_id")


@admin.register(SubjectGroup)
class SubjectGroupAdmin(BaseAdmin):
    admin_priority = 60
    list_display = ("title", "part", "subject_group_id")
    search_fields = ["title", "part", "subject_group_id"]
    ordering = ("title", "part", "subject_group_id")


@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    admin_priority = 10
    list_display = ("name", "description", "order", "show_if_empty")
    search_fields = ["name", "description"]
    ordering = ("name", "description", "order")


@admin.register(SubCategory)
class SubCategoryAdmin(CategoryAdmin):
    admin_priority = 20
    list_display = ("name", "description", "order", "show_if_empty", "parent")
    ordering = ("name", "description", "order", "parent")


@admin.register(SubSubCategory)
class SubSubCategoryAdmin(CategoryAdmin):
    admin_priority = 30
    list_display = ("name", "description", "order", "show_if_empty", "parent")
    ordering = ("name", "description", "order", "parent")


@admin.register(SupplementalContent)
class SupplementalContentAdmin(BaseAdmin):
    admin_priority = 0
    list_display = ("date", "name", "description", "category", "updated_at", "approved")
    search_fields = ["date", "name", "description"]
    ordering = ("-date", "name", "category", "-created_at", "-updated_at")
    filter_horizontal = ("locations",)
    actions = [actions.mark_approved, actions.mark_not_approved]
    list_filter = [
        "approved",
        TitleFilter,
        PartFilter,
        SectionFilter,
        SubpartFilter,
        SubjectGroupFilter,
    ]


def get_app_list(self, request):
    app_dict = self._build_app_dict(request)
    for app_name in app_dict.keys():
        app = app_dict[app_name]
        model_priority = {
            model['object_name']: getattr(
                site._registry[apps.get_model(app_name, model['object_name'])],
                'admin_priority',
                20
            )
            for model in app['models']
        }
        app['models'].sort(key=lambda x: model_priority[x['object_name']])
        yield app


admin.AdminSite.get_app_list = get_app_list
