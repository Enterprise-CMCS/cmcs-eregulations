import re

import requests
from django import forms
from django.conf import settings
from django.contrib import admin
from django.db.models import (
    Prefetch,
)
from django.urls import reverse
from django.utils.html import format_html

from common.functions import establish_client
from content_search.functions import add_to_index
from content_search.models import ContentIndex
from resources.admin import BaseAdmin
from resources.models import AbstractLocation

from .functions import get_upload_link
from .models import AbstractRepoCategory, DocumentType, RepositoryCategory, RepositorySubCategory, Subject, UploadedFile


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


@admin.register(RepositoryCategory)
class CategoryAdmin(BaseAdmin):
    admin_priority = 10
    list_display = ("name", "description", "order", "show_if_empty")
    search_fields = ["name", "description"]
    ordering = ("name", "description", "order")


@admin.register(RepositorySubCategory)
class SubCategoryAdmin(CategoryAdmin):
    admin_priority = 20
    list_display = ("name", "description", "order", "show_if_empty", "parent")
    ordering = ("name", "description", "order", "parent")


class UploadAdminForm(forms.ModelForm):
    file_path = forms.FileField(required=False)

    class Meta:
        model = UploadedFile
        fields = '__all__'


@admin.register(UploadedFile)
class UploadedFileAdmin(BaseAdmin):
    form = UploadAdminForm
    list_display = ("document_name", "index_populated")
    search_fields = ["document_name"]
    ordering = ("document_name",)
    filter_horizontal = ("locations", "subjects")
    readonly_fields = ('download_file', 'file_name', 'get_content', 'index_populated')
    fields = ("file_name", "file_path", "document_name", 'date', 'summary',
              'document_type', 'subjects', 'locations', 'internal_notes',
              'index_populated', 'get_content', 'download_file', 'category',)
    manytomany_lookups = {
        "locations": lambda: AbstractLocation.objects.all().select_subclasses(),
        "subjects": lambda: Subject.objects.all()
    }
    foreignkey_lookups = {
        "category": lambda: AbstractRepoCategory.objects.all().select_subclasses(),
    }

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            Prefetch("category", AbstractRepoCategory.objects.all().select_subclasses()),
        )

    # Will remove any characters from file namess we do not want in it.
    # Commas in file names causes issues in chrsome on downloads since we rename the file.
    def clean_file_name(self, name):
        bad_char = [";", "!", "?", "*", ":", ",", '"', '“', "'", r'/', '\\', '-',]
        temp = ''
        split_name = name.split('.')
        extension = split_name.pop()
        file_name = '.'.join(split_name)
        for i in bad_char:
            temp = temp + i
        clean_name = re.sub(rf'[{temp}]', '', file_name).strip()
        return f'{clean_name}.{extension}'

    def save_model(self, request, obj, form, change):
        path = form.cleaned_data.get("file_path")
        if path:
            obj.file_name = self.clean_file_name(path._name)
            self.upload_file(path, obj)
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        add_to_index(form.instance)

    def upload_file(self, file, obj):
        key = obj.get_key()
        result = get_upload_link(key)
        requests.post(result['url'], data=result['fields'], files={'file': file}, timeout=200)

    def del_file(self, obj):
        s3_client = establish_client('s3')
        key = obj.get_key()

        try:
            s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
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

    def index_populated(self, obj):
        content = ''
        if obj and obj.id:
            index = ContentIndex.objects.get(file=obj)
            content = index.content
        if content:
            return f"Populated: {content[:100]}"
        else:
            return "Not populated"

    def get_content(self, obj):
        if obj.id:
            index = ContentIndex.objects.get(file=obj)
            link = reverse("call-extractor", kwargs={"content_id": index.uid})
            html = '<a class="button" href="{}">Get content</a>'.format(link)
        else:
            return "N/A"
        return format_html(html)
