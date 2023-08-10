from django.contrib import admin

from .models import UploadedFile


class UploadedFileAdmin(admin.ModelAdmin):
    # List of fields to display in the admin list view
    list_display = ('file', 'created_at')
    # Fields to use in the search bar in the admin list view
    search_fields = ('file__name', 'created_at')


# Register the model and custom ModelAdmin class
admin.site.register(UploadedFile, UploadedFileAdmin)
