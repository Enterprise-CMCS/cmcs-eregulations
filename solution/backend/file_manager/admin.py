
from django.conf import settings
from django.contrib import admin
from django import forms
from django.urls import reverse
from django.utils.html import format_html

from resources.admin import BaseAdmin
from resources.models import AbstractLocation

from .functions import establish_client
from .models import DocumentType, Subject, UploadedFile


@admin.register(DocumentType)
class DocumentTypeAdmin(BaseAdmin):
    list_display = ("name", "order",)
    search_fields = ["name",]
    ordering = ("order", "name",)
    fields = ("order", "name", "description",)


@admin.register(Subject)
class SubjectAdmin(BaseAdmin):
    list_display = ("full_name",)
    search_fields = ["full_name", "short_name"]
    ordering = ("full_name", "short_name", "abbreviation")
    fields = ("full_name", "short_name", "abbreviation")

class UploadAdminForm(forms.ModelForm):
    file_path = forms.FileField()
    class Meta:
        model = UploadedFile
        fields = '__all__'
@admin.register(UploadedFile)
class UploadedFileAdmin(BaseAdmin):
    form = UploadAdminForm
    list_display = ("name",)
    search_fields = ["name"]
    ordering = ("name",)
    filter_horizontal = ("locations", "subject")
    readonly_fields = ('download_file',)
    fields = ("name", "file", 'file_path', 'date', 'description',
              'document_type', 'subject', 'locations', 'internal_notes', 'download_file',)
    manytomany_lookups = {
        "locations": lambda: AbstractLocation.objects.all().select_subclasses(),
    }
 #s
    def save_model(self, request, obj, form, change):
        path = form.cleaned_data.get("file_path")
        print(path.__dict__)
        self.upload_file(path)
        super().save_model(request, obj, form, change)
    def upload_file(self, file):
        s3_client = establish_client()
        s3_client.put_object(Body=file,
                             Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                             Key="uploaded_files/" + file._name,
                             ContentType=file.content_type)

    def del_file(self, obj):
        s3_client = establish_client()
        try:
            s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=f"{obj.file.name}")
        except Exception:
            print("Unable to delete")

    def delete_model(self, request, obj):
        try:
            self.del_file(obj)
            obj.delete()
            print('File Deleted')
        except Exception:
            print('Could not delete from server.')

    def download_file(self, obj):
        if obj.id:
            link = reverse("file-download", kwargs={"file_id": obj.uid})
            html = '<input type="button" onclick="location.href=\'{}\'" value="Download File" />'.format(link)
        else:
            return "N/A"
        return format_html(html)
