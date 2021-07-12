from django.contrib import admin

# Register your models here.

from .models import (
    SupplementaryContent,
    Category,
    RegulationSection,
)

class SectionsInline(admin.TabularInline):
    model = RegulationSection.supplementary_content.through

@admin.register(SupplementaryContent)
class SupplementaryContentAdmin(admin.ModelAdmin):
    inlines = [
        SectionsInline,
    ]


class ContentInline(admin.StackedInline):
    model = SupplementaryContent
    extra = 1
    readonly_fields = ("reg_sections",)
    show_change_link = True

    @admin.display(description="Regulation Sections")
    def reg_sections(self, instance):
        section_citations = [f"{s.title} {s.part}.{s.section}" for s in instance.sections.all()]
        return ", ".join(section_citations)


class ChildCategory(admin.StackedInline):
    model = Category
    fk_name = "parent"
    extra = 1
    verbose_name_plural = "Sub-Categories"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [
        ContentInline,
        ChildCategory,
    ]
    list_display = ("title", "parent")


admin.site.register(RegulationSection)
