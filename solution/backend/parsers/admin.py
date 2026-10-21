from django.apps import apps
from django.contrib import admin, messages
from django.db import models, transaction
from django.db.models import Q
from django.forms import TextInput
from django.utils import timezone
from solo.admin import SingletonModelAdmin

from regcore.models import Part

from .models import (
    EcfrLauncherResult,
    EcfrParserResult,
    FrLauncherResult,
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
                    "loglevel",
                    "upload_supplemental_locations",
                    "skip_parsed_regs",
                    "skip_fr_documents",
                ),
                "description": "<b>Please note:</b> Changes to the parser configuration "
                "will not take effect until the next scheduled parser run!",
            },
        ),
    )

    @staticmethod
    def _part_query(target):
        """Build a query for Parts covered by one saved configuration target."""

        title, configuration_type, value = target
        if configuration_type == "part":
            return Q(title=title, name=value)

        if configuration_type == "subchapter":
            chapter, subchapter = value.split("-", 1)
            return Q(
                title=title,
                structure__children__0__type="chapter",
                structure__children__0__identifier=[chapter],
                structure__children__0__children__0__type="subchapter",
                structure__children__0__children__0__identifier=[subchapter],
            )

        return Q(pk__in=[])

    @classmethod
    def _combined_part_query(cls, configurations):
        query = None
        for target in configurations:
            target_query = cls._part_query(target)
            query = target_query if query is None else query | target_query
        return query

    @staticmethod
    def _configuration_target(configuration):
        return configuration.title, configuration.type, configuration.value

    @transaction.atomic
    def save_formset(self, request, form, formset, change):
        previous_targets = [
            self._configuration_target(configuration)
            for configuration in formset.get_queryset()
        ]
        super().save_formset(request, form, formset, change)

        if not previous_targets:
            return

        final_configurations = list(
            PartConfiguration.objects.filter(parser_config_id=form.instance.pk)
        )
        final_targets = {
            configuration.pk: self._configuration_target(configuration)
            for configuration in final_configurations
        }
        previous_query = self._combined_part_query(previous_targets)
        if previous_query is None:
            return

        candidate_parts = Part.objects.filter(previous_query).distinct()
        final_query = self._combined_part_query(final_targets.values())
        affected_parts = candidate_parts
        if final_query is not None:
            affected_parts = affected_parts.exclude(final_query).distinct()

        if affected_parts.exists():
            part_pairs = list(affected_parts.values_list("title", "name").distinct())
            result_filter = Q()
            for title, part in part_pairs:
                result_filter |= Q(title=title, part=part)

            if result_filter.children:
                EcfrParserResult.objects.filter(
                    result_filter,
                    invalidated_at__isnull=True,
                ).update(invalidated_at=timezone.now())

            # If search app is installed, delete relevant search indices and metadata
            search_message = ""
            if apps.is_installed("content_search"):
                from content_search.models import IndexedRegulationText

                deleted_indices = IndexedRegulationText.objects.filter(part__in=affected_parts).delete()
                deleted_by_model = deleted_indices[1]
                search_message = (
                    f", {deleted_by_model.get('content_search.ContentIndex', 0)} search index entries, "
                    f"and {deleted_by_model.get('content_search.IndexedRegulationText', 0)} search metadata entries"
                )

            # Delete affected parts
            part_list = ", ".join([f"{p[0]} CFR {p[1]}" for p in part_pairs])
            deleted_parts = affected_parts.delete()

            deleted_parts_count = deleted_parts[1].get("regcore.Part", 0)
            message = f"Deleted {deleted_parts_count} part instances{search_message} for part(s): {part_list}."

            self.message_user(
                request,
                message,
                level=messages.INFO,
            )


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
    list_display = ("title", "part", "date", "status", "status_updated_at", "invalidated_at", "success", "log_preview")
    list_filter = ("status", "success", "title", "date", "invalidated_at")
    search_fields = ("title", "part", "status", "log")
    readonly_fields = (
        "launcher_result",
        "title",
        "part",
        "date",
        "status",
        "status_updated_at",
        "invalidated_at",
        "timestamp",
        "success",
        "log",
    )


@admin.register(EcfrLauncherResult)
class EcfrLauncherResultAdmin(_ParserResultAdminBase):
    list_display = ("timestamp", "success", "log_preview")
    list_filter = ("success",)
    search_fields = ("log",)
    readonly_fields = ("timestamp", "success", "log")


@admin.register(FrParserResult)
class FrParserResultAdmin(_ParserResultAdminBase):
    list_display = ("document_number", "timestamp", "success", "log_preview")
    list_filter = ("success",)
    search_fields = ("document_number", "log")
    readonly_fields = ("document_number", "timestamp", "success", "log")


@admin.register(FrLauncherResult)
class FrLauncherResultAdmin(_ParserResultAdminBase):
    list_display = ("timestamp", "queued_count", "skipped_count", "failed_count", "success", "log_preview")
    list_filter = ("success",)
    search_fields = ("log",)
    readonly_fields = ("queued_count", "skipped_count", "failed_count", "timestamp", "success", "log")
