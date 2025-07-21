import logging

from django import forms
from django.contrib import admin, messages
from django.db.models import (
    F,
    Prefetch,
    Value,
)
from django.db.models.functions import Concat
from django.urls import reverse
from django.utils.html import escape, format_html

from common.admin import CustomAdminMixin
from common.filters import IndexPopulatedFilter
from resources.models import (
    AbstractCategory,
    AbstractCitation,
    AbstractInternalCategory,
    AbstractPublicCategory,
    ResourcesConfiguration,
    AbstractResource,
)
from resources.utils import (
    call_text_extractor,
    field_changed,
    get_support_link,
)

from . import actions
from .widgets import CustomCategoryChoiceField

logger = logging.getLogger(__name__)

# Abstract resource admin classes.
# Make changes that apply to all resource admin pages, or public or internal pages here.


class AbstractResourceAdmin(CustomAdminMixin, admin.ModelAdmin):
    actions = [actions.mark_approved, actions.mark_not_approved, actions.extract_text]
    filter_horizontal = ["cfr_citations", "subjects"]
    empty_value_display = "NONE"
    ordering = ["-updated_at"]

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

    def save_model(self, request, obj, form, change, *args, **kwargs):
        super().save_model(request, obj, form, change)
        auto_extract = ResourcesConfiguration.get_solo().auto_extract
        if auto_extract and (not change or field_changed(form, "url") or kwargs.pop("force_extract", False)):
            _, fail = call_text_extractor(request, [obj])
            url = f"<a target=\"_blank\" href=\"{reverse('edit', args=[obj.pk])}\">{escape(str(obj))}</a>"
            if fail:
                logger.error("Failed to invoke text extractor for resource with ID %i: %s", obj.pk, fail[0]["reason"])
                message = f"Failed to request text extraction for {obj._meta.verbose_name} \"{url}\". Please ensure "\
                          f"the item has a valid URL or attached file, then {get_support_link('contact support')} "\
                          "for assistance if needed."
                level = messages.WARNING
            else:
                message = f"Text extraction requested for {obj._meta.verbose_name} \"{url}\"."
                level = messages.SUCCESS
            self.message_user(request, format_html(message), level=level)

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
    file_type = forms.CharField(
        max_length=32,
        required=False,
        widget=forms.TextInput(attrs={
            'size': '6',
        }),
        help_text=AbstractResource._meta.get_field('file_type').help_text,
    )


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
