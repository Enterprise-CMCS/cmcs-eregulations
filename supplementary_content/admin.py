from django.contrib import admin
from django.db.models.functions import Cast
from django.db.models import IntegerField

# Register your models here.

from .models import (
    SupplementaryContent,
    Category,
    RegulationSection,
)


class SectionsInline(admin.TabularInline):
    model = RegulationSection.supplementary_content.through

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "regulationsection":
            kwargs["queryset"] = RegulationSection.objects.all().annotate(
                title_int=Cast('title', IntegerField()),
                part_int=Cast('part', IntegerField()),
                section_int=Cast('section', IntegerField())
            ).order_by('title_int', 'part_int', 'section_int')
        return super(SectionsInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(SupplementaryContent)
class SupplementaryContentAdmin(admin.ModelAdmin):
    inlines = [
        SectionsInline,
    ]


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
