from django import forms
from django.db.models import (
    F,
    Prefetch,
    Value,
)
from django.db.models.functions import Concat

from common.admin import AbstractAdmin
from common.filters import IndexPopulatedFilter
from resources.models import (
    AbstractCategory,
    AbstractCitation,
    AbstractInternalCategory,
    AbstractPublicCategory,
)

from . import actions
from .widgets import CustomCategoryChoiceField

# Abstract resource admin classes.
# Make changes that apply to all resource admin pages, or public or internal pages here.


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
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                Prefetch("category", AbstractCategory.objects.all().select_subclasses()),
            )
        )

    # This override allows the grouping post-save hook to work properly.
    # Normally Django saves the model before updating related fields, but this causes aggregates of citations etc to not
    # return the correct data. So we need to save after updating related fields.
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.save()


class AbstractPublicResourceAdmin(AbstractResourceAdmin):
    foreignkey_lookups = {
        "category": lambda: AbstractPublicCategory.objects.all().select_subclasses(),  # Only show public categories
    }


class AbstractInternalResourceAdmin(AbstractResourceAdmin):
    foreignkey_lookups = {
        "category": lambda: AbstractInternalCategory.objects.all().select_subclasses(),  # Only show internal categories
    }


# Abstract resource admin forms.
# Make changes to forms (widgets etc) for all resource admin pages, or public or internal pages here.


class AbstractResourceForm(forms.ModelForm):
    pass


class AbstractPublicResourceForm(AbstractResourceForm):
    category = CustomCategoryChoiceField(
        queryset=AbstractPublicCategory.objects.annotate(sort_name=Concat(F("parent__name"), Value(" "), F("name")))
        .order_by("sort_name")
        .select_subclasses(),
        required=False,
    )


class AbstractInternalResourceForm(AbstractResourceForm):
    category = CustomCategoryChoiceField(
        queryset=AbstractInternalCategory.objects.annotate(sort_name=Concat(F("parent__name"), Value(" "), F("name")))
        .order_by("sort_name")
        .select_subclasses(),
        required=False,
    )
