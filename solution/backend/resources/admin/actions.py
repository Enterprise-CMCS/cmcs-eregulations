import logging

from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html

from resources.utils import call_text_extractor

logger = logging.getLogger(__name__)


@admin.action(description="Mark selected as approved")
def mark_approved(modeladmin, request, queryset):
    queryset.update(approved=True)


@admin.action(description="Mark selected as not approved")
def mark_not_approved(modeladmin, request, queryset):
    queryset.update(approved=False)


@admin.action(description="Extract text from selected resources")
def extract_text(modeladmin, request, queryset):
    success = 0
    failure = []
    for i in queryset:
        try:
            call_text_extractor(request, i)
            success += 1
        except Exception as e:
            logger.error("Failed to invoke text extractor for %s with ID %i: %s", i._meta.verbose_name, i.pk, str(e))
            url = reverse(f"admin:{i._meta.app_label}_{i._meta.model_name}_change", args=[i.pk])
            failure.append(f"<a href=\"{url}\">{i.pk}</a>")

    message = ""
    message += f"Text extraction successfully started on {success} resource{'s' if success > 1 else ''}" if success else ""
    if failure:
        message += ", but " if success else "Text "
        message += f"extraction failed for the following resource{'s' if len(failure) > 1 else ''}: {', '.join(failure)}. "
        message += "Please be sure " + (
            "these items have valid URLs or attached files"
            if len(failure) > 1 else
            "this item has a valid URL or attached file"
        )
        message += ", then contact support for assistance if needed"
    message += "."

    modeladmin.message_user(request, format_html(message), messages.ERROR if failure else messages.SUCCESS)
