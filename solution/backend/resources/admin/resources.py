
from django import forms
from django.db.models import (
    Prefetch,
)
from django.utils import timezone

from common.admin import AbstractAdmin
from common.filters import IndexPopulatedFilter
from resources.models import (
    AbstractCitation,
    AbstractInternalCategory,
    AbstractPublicCategory,
    AbstractCategory,
)

from . import (
    actions,
    widgets,
)

#from resources.serializers.locations import AbstractLocationPolymorphicSerializer


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
            Prefetch("category", AbstractCategory.objects.all().select_subclasses()),
        )

    # Overrides the save method in django admin to handle many to many relationships.
    # Looks at the citations added in bulk uploads and adds them if allowed, sends error message if not.
    def save_related(self, request, form, formsets, change):
        # Compute diff of selected and saved citations for the changelog
        form.cleaned_data["cfr_citations"]
        list(form.instance.cfr_citations.all().select_subclasses())
        #additions = [AbstractLocationPolymorphicSerializer(x).data for x in selection if x not in saved_citations]
        #removals = [AbstractLocationPolymorphicSerializer(x).data for x in saved_citations if x not in selection]
        additions = []
        removals = []

        super().save_related(request, form, formsets, change)

        # Create and append changelog object, if any citations changes occured
        if additions or removals:
            form.instance.cfr_citation_history.append({
                "user": str(request.user),
                "date": str(timezone.now()),
                "additions": additions,
                "removals": removals,
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
    cfr_citation_history = forms.JSONField(
        label="CFR citation history",
        widget=widgets.LocationHistoryWidget(attrs={"rows": 10, "cols": 120}),
        required=False,
        disabled=True,
    )


class AbstractPublicResourceForm(AbstractResourceForm):
    pass


class AbstractInternalResourceForm(AbstractResourceForm):
    pass
