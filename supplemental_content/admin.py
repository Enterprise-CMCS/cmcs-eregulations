from django.contrib import admin

# Register your models here.

from .models import (
    SupplementalContent,
    Category,
    SubCategory,
    SubSubCategory,
    Section,
    SubjectGroup,
    Subpart,
)
from .filters import (
    TitleFilter,
    PartFilter,
    SectionFilter,
    SubpartFilter,
    SubjectGroupFilter,
)


class SupplementalContentInline(admin.TabularInline):
    model = SupplementalContent.locations.through


class BaseAdmin(admin.ModelAdmin):
    list_per_page = 500


@admin.register(Section)
class SectionAdmin(BaseAdmin):
    list_display = ("title", "part", "section_id", "parent")
    search_fields = ["title", "part", "section_id"]
    inlines = [SupplementalContentInline]


@admin.register(Subpart)
class SubpartAdmin(BaseAdmin):
    list_display = ("title", "part", "subpart_id")
    search_fields = ["title", "part", "subpart_id"]


@admin.register(SubjectGroup)
class SubjectGroupAdmin(BaseAdmin):
    list_display = ("title", "part", "subject_group_id")
    search_fields = ["title", "part", "subject_group_id"]


@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    list_display = ("title", "description", "order", "show_if_empty")
    search_fields = ["title", "description"]


@admin.register(SubCategory)
class SubCategoryAdmin(CategoryAdmin):
    list_display = ("title", "description", "order", "show_if_empty", "parent")


@admin.register(SubSubCategory)
class SubSubCategoryAdmin(CategoryAdmin):
    list_display = ("title", "description", "order", "show_if_empty", "parent")


@admin.register(SupplementalContent)
class SupplementalContentAdmin(BaseAdmin):
    list_display = ("date", "title", "description", "category", "created_at", "updated_at")
    search_fields = ["date", "title", "description"]
    filter_horizontal = ("locations",)
    list_filter = [
        "approved",
        TitleFilter,
        PartFilter,
        SectionFilter,
        SubpartFilter,
        SubjectGroupFilter,
    ]
