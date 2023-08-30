
from django.conf import settings
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from resources.admin import BaseAdmin
from resources.models import AbstractLocation

from .functions import establish_client
from .models import Subject, UploadCategory, UploadedFile


@admin.register(UploadCategory)
class UploadCategoriesAdmin(BaseAdmin):
    list_display = ("name", "abbreviation")
    search_fields = ["name", "abbreviation"]
    ordering = ("order", "name")
    fields = ("name", "abbreviation", "description", "order",)


@admin.register(Subject)
class SubjectAdmin(BaseAdmin):
    list_display = ("name",)
    search_fields = ["name"]
    ordering = ("order", "name")
    fields = ("name", "description", "order",)


@admin.register(UploadedFile)
class UploadedFileAdmin(BaseAdmin):
    list_display = ("name",)
    search_fields = ["name"]
    ordering = ("name",)
    filter_horizontal = ("locations", "subject")
    readonly_fields = ('download_file',)
    fields = ("name", "file", 'date', 'description', 'category', 'subject', 'locations', 'download_file',)
    manytomany_lookups = {
        "locations": lambda: AbstractLocation.objects.all().select_subclasses(),
    }

    def del_file(self, obj):
        s3_client = establish_client()
        s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=f"{obj.file.name}")

    def delete_model(self, request, obj):
        try:
            self.del_file(obj)
            obj.delete()
            print('File Deleted')
        except Exception:
            print('Could not delete from server.')

    def download_file(self, obj):
        if obj.id:
            link = reverse("file-download", kwargs={"id": obj.uid})
            html = '<input type="button" onclick="location.href=\'{}\'" value="Download File" />'.format(link)
        else:
            return "N/A"
        return format_html(html)
