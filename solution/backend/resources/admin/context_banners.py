from django.contrib import admin

from common.admin import CustomAdminMixin
from resources.models import AbstractCitation, SectionContextBanner


@admin.register(SectionContextBanner)
class SectionContextBannerAdmin(CustomAdminMixin, admin.ModelAdmin):
    admin_priority = 60
    list_display = ("get_title", "get_part", "get_section", "is_active")
    list_filter = ("citation__title", "citation__part", "is_active")
    search_fields = ("citation__part", "banner_html")
    ordering = ("citation__title", "citation__part", "citation__child_id")
    autocomplete_fields = ("citation",)
    fieldsets = (
        (None, {
            "fields": ("citation", "is_active", "banner_html"),
            "description": "Attach contextual notes to a Section or Subpart.",
        }),
    )

    foreignkey_lookups = {
        "citation": lambda: AbstractCitation.objects.select_subclasses(),
    }

    def get_title(self, obj):
        return obj.citation.title
    get_title.short_description = "Title"

    def get_part(self, obj):
        return obj.citation.part
    get_part.short_description = "Part"

    def get_section(self, obj):
        # For Sections, show section_id; for Subparts, show subpart_id/child_id
        try:
            # Section has attribute section_id; Subpart has subpart_id
            section_string = getattr(obj.citation, "section_id", getattr(obj.citation, "subpart_id", obj.citation.child_id))
            return section_string.lstrip("0")  # Remove leading zeros for display
        except Exception:
            return ""
    get_section.short_description = "Section/Subpart"
