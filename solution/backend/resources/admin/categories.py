from django.contrib import admin

from common.admin import AbstractAdmin
from resources.models import (
    InternalCategory,
    InternalSubCategory,
    PublicCategory,
    PublicSubCategory,
)


class AbstractCategoryAdmin(AbstractAdmin):
    pass


@admin.register(PublicCategory)
class PublicCategoryAdmin(AbstractCategoryAdmin):
    list_display = ["name", "description", "order", "show_if_empty"]
    search_fields = ["name", "description"]
    ordering = ["name", "description", "order"]


@admin.register(PublicSubCategory)
class PublicSubCategoryAdmin(AbstractCategoryAdmin):
    list_display = ["name", "description", "order", "show_if_empty", "parent"]
    search_fields = ["name", "description"]
    ordering = ["name", "description", "order", "parent"]


@admin.register(InternalCategory)
class InternalCategoryAdmin(AbstractCategoryAdmin):
    list_display = ["name", "description", "order", "show_if_empty"]
    search_fields = ["name", "description"]
    ordering = ["name", "description", "order"]


@admin.register(InternalSubCategory)
class InternalSubCategoryAdmin(AbstractCategoryAdmin):
    list_display = ["name", "description", "order", "show_if_empty", "parent"]
    search_fields = ["name", "description"]
    ordering = ["name", "description", "order", "parent"]
