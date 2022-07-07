from django.contrib import admin
from django.contrib.admin.sites import site
from django.apps import apps
from django.urls import path
from django.db.models import Prefetch, Count
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple


# Register your models here.

from .models import (
    SupplementalContent,
    FederalRegisterDocument,
    FederalRegisterCategoryLink,
    AbstractCategory,
    Category,
    SubCategory,
    AbstractLocation,
    Section,
    Subpart,
    FederalRegisterDocumentGroup,
)

from .filters import (
    TitleFilter,
    PartFilter,
    SectionFilter,
    SubpartFilter,
)

from .mixins import ExportCsvMixin
from . import actions


class BaseAdmin(admin.ModelAdmin, ExportCsvMixin):
    change_list_template = "admin/export_all_csv.html"
    list_per_page = 200
    admin_priority = 20
    actions = ["export_as_csv"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        lookups = getattr(self, "foreignkey_lookups", {})
        if db_field.name in lookups:
            kwargs["queryset"] = lookups[db_field.name]()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        lookups = getattr(self, "manytomany_lookups", {})
        if db_field.name in lookups:
            kwargs["queryset"] = lookups[db_field.name]()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

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

    foreignkey_lookups = {
        "parent": lambda: Subpart.objects.all(),
    }

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            Prefetch("parent", AbstractLocation.objects.all().select_subclasses()),
        )


@admin.register(Subpart)
class SubpartAdmin(BaseAdmin):
    admin_priority = 50
    list_display = ("title", "part", "subpart_id")
    search_fields = ["title", "part", "subpart_id"]
    ordering = ("title", "part", "subpart_id")


@admin.register(FederalRegisterCategoryLink)
class FederalRegisterCategoryLinkAdmin(BaseAdmin):
    admin_priority = 100

    foreignkey_lookups = {
        "category": lambda: AbstractCategory.objects.all().select_subclasses(),
    }

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            Prefetch("category", AbstractCategory.objects.all().select_subclasses()),
        )

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + (("name",) if obj else ())  # prevent changing name field on existing objects


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


class AbstractResourceAdmin(BaseAdmin):
    actions = [actions.mark_approved, actions.mark_not_approved]
    filter_horizontal = ("locations",)
    admin_priority = 0
    empty_value_display = "NONE"
    ordering = ("-updated_at", "-date", "name", "category", "-created_at")

    list_filter = [
        "approved",
        TitleFilter,
        PartFilter,
        SectionFilter,
        SubpartFilter,
    ]

    foreignkey_lookups = {
        "category": lambda: AbstractCategory.objects.all().select_subclasses(),
    }

    manytomany_lookups = {
        "locations": lambda: AbstractLocation.objects.all().select_subclasses(),
    }

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            Prefetch("category", AbstractCategory.objects.all().select_subclasses()),
        )


@admin.register(SupplementalContent)
class SupplementalContentAdmin(AbstractResourceAdmin):
    list_display = ("date", "name", "description", "category", "updated_at", "approved")
    list_display_links = ("date", "name", "description", "category", "updated_at")
    search_fields = ["date", "name", "description"]
    fields = ("approved", "name", "description", "date", "url", "category", "locations", "internal_notes")


@admin.register(FederalRegisterDocument)
class FederalRegisterDocumentAdmin(AbstractResourceAdmin):
    list_display = ("date", "name", "description", "docket_numbers", "document_number", "category", "updated_at", "approved")
    list_display_links = ("date", "name", "description", "docket_numbers", "document_number", "category", "updated_at")
    search_fields = ["date", "name", "description", "docket_numbers", "document_number"]
    fields = ("approved", "docket_numbers", "group", "document_number", "name",
              "description", "date", "url", "category", "locations", "internal_notes")


class FederalRegisterDocumentGroupForm(forms.ModelForm):
    documents = forms.ModelMultipleChoiceField(
        queryset=FederalRegisterDocument.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name="Documents",
            is_stacked=False,
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["documents"].initial = self.instance.documents.all()

    def save(self, commit=True):
        group = super().save(commit=False)
        group.documents.set(self.cleaned_data["documents"])
        group.save()
        return group

    class Meta:
        model = FederalRegisterDocumentGroup
        fields = ("docket_number_prefixes", "documents")


@admin.register(FederalRegisterDocumentGroup)
class FederalRegisterDocumentGroupAdmin(BaseAdmin):
    form = FederalRegisterDocumentGroupForm
    admin_priority = 250
    list_display = ("docket_number_prefixes", "number_of_documents")
    list_display_links = ("docket_number_prefixes", "number_of_documents")
    search_fields = ["docket_number_prefixes"]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(number_of_documents=Count("documents"))

    def number_of_documents(self, obj):
        return obj.number_of_documents


# Custom app list function, allows ordering Django Admin models by "admin_priority", low to high
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


# Patch Django's built in get_app_list function
admin.AdminSite.get_app_list = get_app_list
