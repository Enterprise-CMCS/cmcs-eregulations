from django.contrib import admin
from django.db import models
from django.forms import ModelChoiceField
from django.utils.html import format_html


class CustomCategoryChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return format_html("&nbsp;&nbsp;&nbsp;&nbsp;{}", obj.name) if "Subcategory" in obj._meta.verbose_name else obj.name


class AbstractAdmin(admin.ModelAdmin):
    list_per_page = 200
    admin_priority = 20
    formfield_overrides = {
        models.ForeignKey: {"form_class": CustomCategoryChoiceField},
    }

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
