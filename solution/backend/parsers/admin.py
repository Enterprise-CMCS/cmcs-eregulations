from django.apps import apps
from django.contrib import admin, messages
from django.db import models
from django.db.models import Q
from django.forms import TextInput
from solo.admin import SingletonModelAdmin

from regcore.models import Part

from .models import (
    EcfrParserResult,
    FrParserResult,
    ParserConfiguration,
    PartConfiguration,
)


class PartConfigurationInline(admin.TabularInline):
    ordering = ("title", "value")
    formfield_overrides = {
        models.TextField: {
            "widget": TextInput(attrs={
                "style": "width: calc(100% - 1em);",
            })
        }
    }
    model = PartConfiguration
    extra = 0


@admin.register(ParserConfiguration)
class ParserConfigurationAdmin(SingletonModelAdmin):
    inlines = (PartConfigurationInline,)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "workers",
                    "loglevel",
                    "upload_supplemental_locations",
                    "log_parse_errors",
                    "skip_reg_versions",
                    "skip_fr_documents",
                ),
                "description": "<b>Please note:</b> Changes to the parser configuration "
                "will not take effect until the next scheduled parser run!",
            },
        ),
    )

    def save_formset(self, request, form, formset, change):
        formset.save(commit=False)

        # Generate a filter to find all affected parts
        q = Q()
        for obj in [i for i in formset.deleted_objects if isinstance(i, PartConfiguration)]:
            if obj.type == "part":
                q |= Q(title=obj.title, name=obj.value)  # Direct part match
            elif obj.type == "subchapter":
                # Find all parts under this subchapter
                chapter, subchapter = obj.value.split("-")
                exclude = list(PartConfiguration.objects.filter(title=obj.title, type="part").values_list("value", flat=True))
                q |= (
                    Q(
                        title=obj.title,
                        structure__children__0__type="chapter",
                        structure__children__0__identifier=[chapter],
                        structure__children__0__children__0__type="subchapter",
                        structure__children__0__children__0__identifier=[subchapter],
                    )
                    & ~Q(name__in=exclude)
                )

        affected_parts = Part.objects.filter(q).distinct()
        if affected_parts.exists():
            # If search app is installed, delete relevant search indices and metadata
            search_message = ""
            if apps.is_installed("content_search"):
                from content_search.models import IndexedRegulationText

                deleted_indices = IndexedRegulationText.objects.filter(part__in=affected_parts).delete()
                search_message = (
                    f", {deleted_indices[1]['content_search.ContentIndex']} search index entries, "
                    f"and {deleted_indices[1]['content_search.IndexedRegulationText']} search metadata entries"
                )

            # Delete affected parts
            part_list = affected_parts.distinct("title", "name").values_list("title", "name")
            part_list = ", ".join([f"{p[0]} CFR {p[1]}" for p in part_list])
            deleted_parts = affected_parts.delete()

            message = f"Deleted {deleted_parts[1]['regcore.Part']} part instances{search_message} for part(s): {part_list}."

            self.message_user(
                request,
                message,
                level=messages.INFO,
            )

        super().save_formset(request, form, formset, change)


class _ParserResultAdminBase(admin.ModelAdmin):
    ordering = ("-timestamp",)
    date_hierarchy = "timestamp"

    def has_add_permission(self, request):
        return False

    @admin.display(description="log")
    def log_preview(self, obj):
        if not obj.log:
            return ""
        return f"{obj.log[:80]}..." if len(obj.log) > 80 else obj.log


@admin.register(EcfrParserResult)
class EcfrParserResultAdmin(_ParserResultAdminBase):
    list_display = ("title", "part", "date", "timestamp", "success", "log_preview")
    list_filter = ("success", "title", "date")
    search_fields = ("title", "part", "log")
    readonly_fields = ("title", "part", "date", "timestamp", "success", "log")


@admin.register(FrParserResult)
class FrParserResultAdmin(_ParserResultAdminBase):
    list_display = ("document_number", "timestamp", "success", "log_preview")
    list_filter = ("success",)
    search_fields = ("document_number", "log")
    readonly_fields = ("document_number", "timestamp", "success", "log")
