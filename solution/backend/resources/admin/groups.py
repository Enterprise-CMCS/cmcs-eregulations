from django.contrib import admin
from django.db.models import Count

from common.admin import AbstractAdmin
from resources.models import (
    AbstractResource,
    ResourceGroup,
)


@admin.register(ResourceGroup)
class ResourceGroupAdmin(AbstractAdmin):
    admin_priority = 50
    list_display = ["name", "common_identifiers", "number_of_resources"]
    list_display_links = ["name", "common_identifiers", "number_of_resources"]
    search_fields = ["name", "common_identifiers"]

    fields = ["name", "common_identifiers", "resources"]
    filter_horizontal = ["resources"]

    manytomany_lookups = {
        "resources": lambda: AbstractResource.objects.all().select_subclasses(),
    }

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            number_of_resources=Count("resources")
        )

    def number_of_resources(self, obj):
        return obj.number_of_resources

    # This override allows the grouping post-save hook to work properly.
    # Normally Django saves the model before updating related fields, but this causes aggregates of citations etc to not
    # return the correct data. So we need to save after updating related fields.
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.save()
