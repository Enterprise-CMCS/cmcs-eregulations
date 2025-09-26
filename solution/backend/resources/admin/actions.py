import logging

from django.apps import apps
from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html

from resources.utils import get_support_link

logger = logging.getLogger(__name__)


@admin.action(description="Mark selected as approved")
def mark_approved(modeladmin, request, queryset):
    queryset.update(approved=True)


@admin.action(description="Mark selected as not approved")
def mark_not_approved(modeladmin, request, queryset):
    queryset.update(approved=False)


@admin.action(description="Extract text from selected resources")
def extract_text(modeladmin, request, queryset):
    if not apps.is_installed("content_search"):
        modeladmin.message_user(
            request,
            "The Content Search app is not installed, so text extraction cannot be performed.",
            messages.ERROR,
        )
        return

    from content_search.utils import call_text_extractor_for_resources  # Imported here to avoid circular import issues

    successes, failures = call_text_extractor_for_resources(request, queryset)

    failure_urls = []
    for i in failures:
        logger.error("Failed to invoke text extractor for resource with ID %i: %s", i["id"], i["reason"])
        url = reverse("edit", args=[i["id"]])
        failure_urls.append(f"<a target=\"_blank\" href=\"{url}\">{i['id']}</a>")

    if successes:
        modeladmin.message_user(
            request,
            format_html(f"Text extraction requested for {successes} resource{'s' if successes > 1 else ''}."),
            messages.SUCCESS,
        )

    if failures:
        message = f"Failed to request text extraction for the following resource{'s' if len(failures) > 1 else ''}: "
        message += f"{', '.join(failure_urls)}. Please be sure " + (
            "these items have valid URLs or attached files"
            if len(failures) > 1 else
            "this item has a valid URL or attached file"
        ) + f", then {get_support_link('contact support')} for assistance if needed."
        modeladmin.message_user(request, format_html(message), messages.ERROR)
