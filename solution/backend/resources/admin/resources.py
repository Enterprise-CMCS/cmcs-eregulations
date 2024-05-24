import csv
import json
import re

from django import forms
from django.contrib import admin, messages
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import (
    Case,
    Count,
    F,
    Prefetch,
    Value,
    When,
)
from django.forms.widgets import Textarea
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path, reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from solo.admin import SingletonModelAdmin

from common.filters import IndexPopulatedFilter
from content_search.functions import add_to_index
from content_search.models import ContentIndex


from common.admin import AbstractAdmin
from . import (
    actions,
    widgets,
)
from resources.models import (
    PublicLink,
    FederalRegisterLink,
    InternalFile,
    InternalLink,
    NewAbstractCategory,
    AbstractPublicCategory,
    AbstractCitation,
)

from resources.serializers.locations import AbstractLocationPolymorphicSerializer


class AbstractResourceAdmin(AbstractAdmin):
    actions = [actions.mark_approved, actions.mark_not_approved]
    filter_horizontal = ["cfr_citations", "subjects"]
    empty_value_display = "NONE"
    ordering = ["-updated_at", "date", "document_id", "category", "-created_at"]

    list_filter = [
        "approved",
        IndexPopulatedFilter,
    ]

    manytomany_lookups = {
        "cfr_citations": lambda: AbstractCitation.objects.all().select_subclasses(),
    }

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            Prefetch("category", NewAbstractCategory.objects.all().select_subclasses()),
        )

    # Retrieves a citation object if it exists, otherwise None.
    # Valid sections: 42 433.1, 42 CFR 433.1, 42 433 1
    # Valid subparts: 42 433.A, 42 CFR 433 Subpart A, 42 CFR 433.A, 42 433 A
    # All inputs can have no title (i.e. 433.1 instead of 42 CFR 433.1, etc.)
    def get_citation(self, citation, default_title):
        CITATION_REGEX = r"^(?:([0-9]+)\s+(?:cfr)?(?:\s+)?)?([0-9]+)(?:(?:[\s]+|[.])([0-9]+)"\
                         r"|(?:\.|\s+(?:subpart\s+)?)((?!subpart)[a-z]+))$"
        match = re.search(CITATION_REGEX, citation, re.IGNORECASE)
        if not match:
            return None

        title, part, section, subpart = match.groups()
        title = title or default_title

        kwargs = {
            **{"title": title, "part": part},
            **({"newsection__section_id": section} if section else {"newsubpart__subpart_id": subpart}),  # TODO: newsection->section, same for subpart
        }

        try:
            return AbstractCitation.objects.get_subclass(**kwargs)
        except AbstractCitation.DoesNotExist:
            return None

    def get_bulk_citations(self, bulk_citations, bulk_title=""):
        bulk_adds = []
        bad_citations = []
        for cit_id in [i.strip() for i in bulk_citations.split(",")]:
            citation = self.get_citation(cit_id, bulk_title)
            if citation:
                bulk_adds.append(citation)
            else:
                bad_citations.append(cit_id)
        return bulk_adds, bad_citations

    # Overrides the save method in django admin to handle many to many relationships.
    # Looks at the citations added in bulk uploads and adds them if allowed, sends error message if not.
    def save_related(self, request, form, formsets, change):
        # Compute diff of selected and saved citations for the changelog
        selection = form.cleaned_data["cfr_citations"]
        saved_citations = list(form.instance.cfr_citations.all().select_subclasses())
        additions = [AbstractLocationPolymorphicSerializer(x).data for x in selection if x not in saved_citations]
        removals = [AbstractLocationPolymorphicSerializer(x).data for x in saved_citations if x not in selection]

        bulk_citations = form.cleaned_data.get("bulk_citations")
        bulk_title = form.cleaned_data.get("bulk_title")
        bad_citations = []
        bulk_adds = []
        bulk_cits = []

        super().save_related(request, form, formsets, change)
        if bulk_citations:
            bulk_adds, bad_citations = self.get_bulk_citations(bulk_citations, bulk_title)
            if bad_citations:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"The following CFR citations could not be added: {', '.join(bad_citations)}",
                )
            if bulk_adds:
                for citation in bulk_adds:
                    form.instance.cfr_citations.add(citation)
                    bulk_cits.append(AbstractLocationPolymorphicSerializer(citation).data)

        # Create and append changelog object, if any citations changes occured
        if additions or removals or bulk_adds:
            form.instance.cfr_citation_history.append({
                "user": str(request.user),
                "date": str(timezone.now()),
                "additions": additions,
                "removals": removals,
                "bulk_adds": bulk_cits,
            })
            form.instance.save()


class AbstractPublicResourceAdmin(AbstractResourceAdmin):
    foreignkey_lookups = {
        "category": lambda: AbstractPublicCategory.objects.all().select_subclasses(),  # Only show public categories
    }


class AbstractInternalResourceAdmin(AbstractResourceAdmin):
    foreignkey_lookups = {
        "category": lambda: AbstractInternalCategory.objects.all().select_subclasses(),  # Only show internal categories
    }


class AbstractResourceForm(forms.ModelForm):
    bulk_title = forms.IntegerField(
        required=False,
        help_text="If any bulk locations are missing a title, add it here.",
    )

    bulk_citations = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text=mark_safe(
            "Add a list of locations separated by a comma. For example: \"42 CFR 430.10, 42 430 Subpart B, 45 18.150\". "
            "<a href=\"https://docs.google.com/document/d/1HKjg5pUQnRP98i9xbGy0fPiGq_0a6p2PRXhwuDbmiek/edit#\" target=\"blank\">"
            "Click here for detailed documentation.</a>"
        ),
    )

    cfr_citation_history = forms.JSONField(
        label="CFR citation history",
        widget=widgets.LocationHistoryWidget(attrs={"rows": 10, "cols": 120}),
        required=False,
        disabled=True,
    )

    # TODO: check desired behavior of and implement duplicate document checking


class AbstractPublicResourceForm(AbstractResourceForm):
    pass


class AbstractInternalResourceForm(AbstractResourceForm):
    pass
