from django.contrib import admin
from django.db.models import Q

from .models import (
    SupplementaryContent,
    Category,
    RegulationSection,
)
from .filters import (
    TitleFilter,
    PartFilter,
    SectionFilter,
)


class SectionsInline(admin.TabularInline):
    model = RegulationSection.supplementary_content.through


@admin.register(SupplementaryContent)
class SupplementaryContentAdmin(admin.ModelAdmin):
    inlines = [
        SectionsInline,
    ]
    list_filter = (
        "approved",
        TitleFilter,
        PartFilter,
        SectionFilter,
    )


class ChildCategory(admin.StackedInline):
    model = Category
    fk_name = "parent"
    extra = 1
    verbose_name_plural = "Sub-Categories"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [
        ChildCategory,
    ]
    list_display = ("title", "parent")


admin.site.register(RegulationSection)
