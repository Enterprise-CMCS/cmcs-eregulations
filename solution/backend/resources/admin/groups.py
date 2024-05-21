from django.contrib import admin
from django.db.models import Count

from common.admin import AbstractAdmin
from resources.models import (
    NewAbstractResource,
    ResourceGroup,
)


@admin.register(ResourceGroup)
class ResourceGroupAdmin(AbstractAdmin):
    list_display = ["document_id", "common_identifiers", "number_of_resources"]
    list_display_links = ["document_id", "common_identifiers", "number_of_resources"]
    search_fields = ["document_id", "common_identifiers"]

    fields = ["document_id", "common_identifiers", "resources"]
    filter_horizontal = ["resources"]

    manytomany_lookups = {
        "resources": lambda: NewAbstractResource.objects.all().select_subclasses(),
    }

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            number_of_resources=Count("resources")
        )

    def number_of_resources(self, obj):
        return obj.number_of_resources
