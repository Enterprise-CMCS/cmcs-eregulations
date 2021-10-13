from django.contrib import admin
from django.db.models.functions import Cast
from django.db.models import IntegerField, ManyToManyField
from django.contrib.admin.widgets import FilteredSelectMultiple

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
)


class BaseAdmin(admin.ModelAdmin):
    list_per_page = 500


@admin.register(Section)
class SectionAdmin(BaseAdmin):
    list_display = ("title", "part", "section_id", "parent")
    search_fields = ["title", "part", "section_id"]


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
    list_display = ("title", "truncated_description", "order", "show_if_empty")
    search_fields = ["title", "description"]


@admin.register(SubCategory)
class SubCategoryAdmin(CategoryAdmin):
    list_display = ("title", "truncated_description", "order", "show_if_empty", "parent")


@admin.register(SubSubCategory)
class SubSubCategoryAdmin(CategoryAdmin):
    list_display = ("title", "truncated_description", "order", "show_if_empty", "parent")


@admin.register(SupplementalContent)
class SupplementalContentAdmin(BaseAdmin):
    list_display = ("date", "title", "truncated_description", "category", "created_at", "updated_at")
    search_fields = ["date", "title", "truncated_description"]
