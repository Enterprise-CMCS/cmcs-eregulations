from django import forms
from django.contrib import admin
from django.db.models import Prefetch

from resources.models import (
    FederalRegisterLink,
    PublicLink,
    ResourceGroup,
)

from .resources import (
    AbstractPublicResourceAdmin,
    AbstractPublicResourceForm,
)


class PublicLinkForm(AbstractPublicResourceForm):
    pass


@admin.register(PublicLink)
class PublicLinkAdmin(AbstractPublicResourceAdmin):
    admin_priority = 10
    form = PublicLinkForm
    list_display = ["date", "document_id", "title", "category", "updated_at", "approved"]
    list_display_links = ["date", "document_id", "title", "category", "updated_at", "approved"]
    search_fields = ["date", "document_id", "title", "url"]

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
        ("Document status", {
            "fields": ["approved"],
        }),
    ]


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
                    "category", "action_type", "updated_at", "approved"]
    list_display_links = ["date", "document_id", "title", "in_groups", "docket_numbers", "document_number",
                          "category", "action_type", "updated_at", "approved"]
    search_fields = ["date", "document_id", "title", "docket_numbers", "document_number", "url"]

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
        ("Document status", {
            "fields": ["approved"],
        }),
    ]

    def in_groups(self, obj):
        groups = ", ".join([str(i) for i in obj.resource_groups.all()])
        return f"{groups[:20]}..." if len(groups) > 20 else groups

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            Prefetch("resource_groups", ResourceGroup.objects.all()),
        )

    def save_model(self, request, obj, form, change):
        if change and form.initial.get("url") != form.cleaned_data.get("url"):
            # Attempt to use the Federal Register API to retrieve the document's extract_url parameter
            pass
        super().save_model(request, obj, form, change)

    # Override document_id's default help_text to show specific FR link information
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['document_id'].help_text = \
            "This is the citation number for the rule. It usually looks like this: \"55 FR 10938\", " \
            "where \"55\" is the volume number and \"10938\" is the page number."
        return form
