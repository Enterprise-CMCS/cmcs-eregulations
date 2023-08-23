from .models import UploadedFile
from django.contrib import admin, messages


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ["name"]
    ordering = ("name",)
    fields = ("name", "file",)

