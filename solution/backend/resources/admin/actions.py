import logging

from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html

from resources.utils import call_text_extractor, get_support_link

logger = logging.getLogger(__name__)


@admin.action(description="Mark selected as approved")
def mark_approved(modeladmin, request, queryset):
    queryset.update(approved=True)


@admin.action(description="Mark selected as not approved")
def mark_not_approved(modeladmin, request, queryset):
    queryset.update(approved=False)


@admin.action(description="Extract text from selected resources")
def extract_text(modeladmin, request, queryset):
    successes, failures = call_text_extractor(request, queryset)

    failure_urls = []
    for i in failures:
        logger.error("Failed to invoke text extractor for resource with ID %i: %s", i["id"], i["reason"])
        url = reverse("edit", args=[i["id"]])
        failure_urls.append(f"<a target=\"_blank\" href=\"{url}\">{i['id']}</a>")

    message = ""
    message += f"Text extraction successfully started on {successes} resource{'s' if successes > 1 else ''}" if successes else ""
    if failures:
        message += ", but " if successes else "Text "
        message += f"extraction failed for the following resource{'s' if len(failures) > 1 else ''}: {', '.join(failure_urls)}. "
        message += "Please be sure " + (
            "these items have valid URLs or attached files"
            if len(failures) > 1 else
            "this item has a valid URL or attached file"
        )
        message += f", then {get_support_link('contact support')} for assistance if needed"
    message += "."

    modeladmin.message_user(request, format_html(message), messages.ERROR if failures else messages.SUCCESS)
