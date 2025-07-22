import json
import logging

import requests
from django import forms
from django.contrib import admin, messages
from django.db.models import Prefetch
from django.utils.html import format_html

from resources.models import (
    FederalRegisterLink,
    PublicLink,
    ResourceGroup,
)
from resources.utils import field_changed, get_support_link

from .resources import (
    AbstractPublicResourceAdmin,
    AbstractPublicResourceForm,
)

logger = logging.getLogger(__name__)


class PublicLinkForm(AbstractPublicResourceForm):
    pass


@admin.register(PublicLink)
class PublicLinkAdmin(AbstractPublicResourceAdmin):
    admin_priority = 10
    form = PublicLinkForm
    list_display = ["date", "document_id", "title", "category__name", "updated_at", "approved"]
    list_display_links = ["date", "document_id", "title", "updated_at"]
    search_fields = ["date", "document_id", "title", "url"]
    readonly_fields = ["indexing_status", "detected_file_type"]

    fieldsets = [
        ("Basics", {
            "fields": ["url", "title"],
        }),
        ("Details", {
            "fields": ["date", "document_id", "editor_notes"],
        }),
        ("Categorization", {
            "fields": ["category", "subjects"],
        }),
        ("Related citations", {
            "fields": ["cfr_citations", ("act_citations", "usc_citations")],
        }),
        ("Search indexing", {
            "classes": ("collapse",),
            "fields": ["indexing_status", "detected_file_type", "file_type", "extract_text"],
        }),
        ("Document status", {
            "fields": ["approved"],
        }),
    ]

    class Media:
        css = {
            'all': ('css/admin/custom_admin.css',)
        }


class FederalRegisterLinkForm(AbstractPublicResourceForm):
    resource_groups = forms.ModelMultipleChoiceField(
        ResourceGroup.objects.all(),
        widget=admin.widgets.FilteredSelectMultiple('groups', is_stacked=False),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # Populate the FilteredSelectMultiple widget for resource groups
            self.initial['resource_groups'] = self.instance.resource_groups.all()

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        if not instance.pk:
            instance.save()
        # Add groups to the resource_groups ManyToMany
        instance.resource_groups.clear()
        instance.resource_groups.add(*self.cleaned_data['resource_groups'])
        return instance


@admin.register(FederalRegisterLink)
class FederalRegisterLinkAdmin(AbstractPublicResourceAdmin):
    admin_priority = 11
    form = FederalRegisterLinkForm
    list_display = ["date", "document_id", "title", "in_groups", "docket_numbers", "document_number",
                    "action_type", "updated_at", "approved"]
    list_display_links = ["date", "document_id", "title", "docket_numbers", "document_number", "updated_at"]
    search_fields = ["date", "document_id", "title", "docket_numbers", "document_number", "url"]
    readonly_fields = ["indexing_status", "detected_file_type"]

    fieldsets = [
        ("Basics", {
            "fields": ["url", "title"],
        }),
        ("Details", {
            "fields": ["date", "document_id", "document_number", "docket_numbers", "resource_groups",
                       "action_type", ("correction", "withdrawal"), "editor_notes"],
        }),
        ("Categorization", {
            "fields": ["category", "subjects"],
        }),
        ("Related citations", {
            "fields": ["cfr_citations", ("act_citations", "usc_citations")],
        }),
        ("Search indexing", {
            "classes": ("collapse",),
            "fields": ["indexing_status", "detected_file_type", "file_type"],
        }),
        ("Document status", {
            "fields": ["approved"],
        }),
    ]

    class Media:
        css = {
            'all': ('css/admin/custom_admin.css',)
        }

    def in_groups(self, obj):
        groups = ", ".join([str(i) for i in obj.resource_groups.all()])
        return f"{groups[:20]}..." if len(groups) > 20 else groups

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            Prefetch("resource_groups", ResourceGroup.objects.all()),
        )

    def save_model(self, request, obj, form, change):
        force_extract = False
        if not change or field_changed(form, "document_number") or field_changed(form, "url"):
            # Attempt to use the Federal Register's API to retrieve the document's raw text URL
            try:
                document_number = form.cleaned_data.get("document_number")
                response = requests.get(
                    f"https://www.federalregister.gov/api/v1/documents/{document_number}.json",
                    timeout=10,
                )
                response.raise_for_status()
                content = json.loads(response.content)
                obj.extract_url = content["raw_text_url"]
                force_extract = True
            except Exception as e:
                # This can be due to a bad document_number, a network error, or a JSON parse error due to an invalid response.
                # We handle all cases in the same way: show a warning to the user, log the error, then finally save the model.
                logger.warning("Failed to retrieve the raw text URL for Federal Register Link \"%s\": %s", document_number, e)
                message = "Failed to retrieve the URL used for extracting raw text from the Federal Register. "\
                          f"Please check the document number and try again, or {get_support_link('contact support')} "\
                          "for assistance."
                self.message_user(request, format_html(message), level=messages.WARNING)
        super().save_model(request, obj, form, change, force_extract=force_extract)

    # Override document_id's default help_text to show specific FR link information
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['document_id'].help_text = \
            "This is the citation number for the rule. It usually looks like this: \"55 FR 10938\", " \
            "where \"55\" is the volume number and \"10938\" is the page number."
        return form
