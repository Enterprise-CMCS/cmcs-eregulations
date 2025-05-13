from django.contrib import admin
from django.db.models import Prefetch

from common.admin import CustomAdminMixin
from resources.models import (
    AbstractCategory,
    InternalCategory,
    InternalSubCategory,
    PublicCategory,
    PublicSubCategory,
)


class AbstractCategoryAdmin(CustomAdminMixin, admin.ModelAdmin):
    pass


@admin.register(PublicCategory)
class PublicCategoryAdmin(AbstractCategoryAdmin):
    admin_priority = 30
    exclude = ["parent"]
    list_display = ["name", "description", "order", "show_if_empty"]
    search_fields = ["name", "description"]
    ordering = ["name", "description", "order"]


@admin.register(PublicSubCategory)
class PublicSubCategoryAdmin(AbstractCategoryAdmin):
    admin_priority = 31
    list_display = ["name", "description", "order", "show_if_empty", "parent"]
    search_fields = ["name", "description"]
    ordering = ["name", "description", "order", "parent"]

    foreignkey_lookups = {
        "parent": lambda: PublicCategory.objects.all(),
    }

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                Prefetch("parent", AbstractCategory.objects.select_subclasses()),
            )
        )


@admin.register(InternalCategory)
class InternalCategoryAdmin(AbstractCategoryAdmin):
    admin_priority = 32
    exclude = ["parent"]
    list_display = ["name", "description", "order", "show_if_empty"]
    search_fields = ["name", "description"]
    ordering = ["name", "description", "order"]


@admin.register(InternalSubCategory)
class InternalSubCategoryAdmin(AbstractCategoryAdmin):
    admin_priority = 33
    list_display = ["name", "description", "order", "show_if_empty", "parent"]
    search_fields = ["name", "description"]
    ordering = ["name", "description", "order", "parent"]

    foreignkey_lookups = {
        "parent": lambda: InternalCategory.objects.all(),
    }

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                Prefetch("parent", AbstractCategory.objects.select_subclasses()),
            )
        )
