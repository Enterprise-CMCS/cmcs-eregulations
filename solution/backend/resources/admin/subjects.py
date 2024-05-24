from django.contrib import admin

from common.admin import AbstractAdmin
from resources.models import NewSubject

@admin.register(NewSubject)
class NewSubjectAdmin(AbstractAdmin):
    list_display = ["full_name", "short_name", "abbreviation"]
    search_fields = ["full_name", "short_name", "abbreviation"]
    ordering = ["full_name", "short_name", "abbreviation"]
    fields = ["full_name", "short_name", "abbreviation", "description"]
