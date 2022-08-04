from django.contrib import admin
from django.contrib.admin.sites import site
from django.apps import apps
from django.urls import path
from django.db.models import Prefetch
from django import forms
from django.contrib import messages
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


class SupContentForm(forms.ModelForm):
    class Meta:
        model = SupplementalContent
        fields = "__all__"

    bulk_title = forms.CharField(required=False, help_text="If bulk locations is missing a title, add it here.")
    bulk_locations = forms.CharField(
                        widget=forms.Textarea,
                        required=False,
                        help_text="Add a list of locations seperated by a comma.  ex. 42 430.10, 42 430 Subpart B, 45 18.150")

    def save(self, commit=True):
        return super(SupContentForm, self).save(commit=commit)


@admin.register(SupplementalContent)
class SupplementalContentAdmin(AbstractResourceAdmin):
    form = SupContentForm
    list_display = ("date", "name", "description", "category", "updated_at", "approved")
    list_display_links = ("date", "name", "description", "category", "updated_at")
    search_fields = ["date", "name", "description"]
    fields = ("approved", "name", "description", "date", "url", "category",
              "locations", "bulk_title", "bulk_locations", "internal_notes")

    def save_related(self, request, form, formsets, change):
        bulk_locations = form.cleaned_data.get("bulk_locations")
        bulk_title = form.cleaned_data.get("bulk_title")
        bad_locations = []
        
        super().save_related(request, form, formsets, change)
        if bulk_locations:
            split_locations = bulk_locations.split(",")
            for location in split_locations:
                a = self.build_location(location.strip(), bulk_title)
                if a:
                    form.instance.locations.add(a)
                else:
                    bad_locations.append(location)
            if bad_locations:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "The following locations were not added %s" % ((", ").join(bad_locations))
                )

    def build_location(self, location, default_title):
        found_location = location.split(" ")
        if len(found_location) == 1 or len(found_location) == 2:
            if default_title != "":
                title = default_title
                part = location.split(".")[0]
                section = location.split(".")[1]
            else:
                title = found_location[0]
                part = found_location[1].split(".")[0]
                section = found_location[1].split(".")[1]
            if self.check_values(title, part, section, ""):
                try:
                    return Section.objects.get(title=title, part=part, section_id=section).abstractlocation_ptr
                except Section.DoesNotExist:
                    return None

        elif len(found_location) == 3 or len(found_location) == 4:
            if default_title != "":
                title = default_title
                part = found_location[0]
                subpart = found_location[2]
            else:
                title = found_location[0]
                part = found_location[1]
                subpart = found_location[3]
            if self.check_values(title, part, "", subpart):
                try:
                    return Subpart.objects.get(title=title, part=part, subpart_id=subpart).abstractlocation_ptr
                except Subpart.DoesNotExist:
                    return None

        return None

    def check_values(self, title, part, section, subpart):
        if not title.isdigit() or not part.isdigit():
            return False
        if section != "" and not section.isdigit():
            return False
        if subpart != "" and not isinstance(subpart, str):
            return False
        return True


@admin.register(FederalRegisterDocument)
class FederalRegisterDocumentAdmin(AbstractResourceAdmin):
    list_display = ("date", "name", "description", "docket_number", "document_number", "category", "updated_at", "approved")
    list_display_links = ("date", "name", "description", "docket_number", "document_number", "category", "updated_at")
    search_fields = ["date", "name", "description", "docket_number", "document_number"]
    fields = ("approved", "docket_number", "document_number", "name",
              "description", "date", "url", "category", "locations", "internal_notes")


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
