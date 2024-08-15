from django.contrib import admin

from common.admin import CustomAdminMixin
from resources.models import Subject


@admin.register(Subject)
class SubjectAdmin(CustomAdminMixin, admin.ModelAdmin):
    admin_priority = 40
    list_display = ["full_name", "short_name", "abbreviation"]
    search_fields = ["full_name", "short_name", "abbreviation"]
    ordering = ["full_name", "short_name", "abbreviation"]
    fields = ["full_name", "short_name", "abbreviation", "description"]
