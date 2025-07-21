import requests
from django import forms
from django.conf import settings
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from resources.models import (
    InternalFile,
    InternalLink,
)
from resources.utils import establish_client

from .resources import (
    AbstractInternalResourceAdmin,
    AbstractInternalResourceForm,
)


class InternalLinkForm(AbstractInternalResourceForm):
    pass


@admin.register(InternalLink)
class InternalLinkAdmin(AbstractInternalResourceAdmin):
    admin_priority = 20
    form = InternalLinkForm
    list_display = ["date", "document_id", "title", "category__name", "updated_at", "approved"]
    list_display_links = ["date", "document_id", "title", "updated_at"]
    search_fields = ["date", "document_id", "title", "summary"]
    readonly_fields = ["indexing_status", "detected_file_type"]

    fieldsets = [
        ("Basics", {
            "fields": ["url", "title"],
        }),
        ("Details", {
            "fields": ["date", "document_id", "summary", "editor_notes"],
        }),
        ("Categorization", {
            "fields": ["category", "subjects"],
        }),
        ("Related citations", {
            "fields": ["cfr_citations", ("act_citations", "usc_citations")],
        }),
        ("Search indexing", {
            "classes": ("collapse",),
            "fields": ["indexing_status", "detected_file_type", "file_type"],
        }),
        ("Document status", {
            "fields": ["approved"],
        }),
    ]

    class Media:
        css = {
            'all': ('css/admin/custom_admin.css',)
        }

    # Override the URL field's help_text for internal links specifically
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['url'].help_text = \
            "To link to an existing document - for example in Box or SharePoint - enter the full URL here."
        return form


class InternalFileForm(AbstractInternalResourceForm):
    file_upload = forms.FileField(required=False)


@admin.register(InternalFile)
class InternalFileAdmin(AbstractInternalResourceAdmin):
    admin_priority = 21
    form = InternalFileForm
    list_display = ["date", "document_id", "title", "category__name", "updated_at", "approved"]
    list_display_links = ["date", "document_id", "title", "updated_at"]
    search_fields = ["date", "document_id", "title", "summary"]
    readonly_fields = ["download_file", "file_name", "indexing_status", "detected_file_type"]

    fieldsets = [
        ("Basics", {
            "fields": ["file_name", "file_upload", "title"],
        }),
        ("Details", {
            "fields": ["date", "document_id", "summary", "editor_notes"],
        }),
        ("Categorization", {
            "fields": ["category", "subjects"],
        }),
        ("Related citations", {
            "fields": ["cfr_citations", ("act_citations", "usc_citations")],
        }),
        ("Search indexing", {
            "classes": ("collapse",),
            "fields": ["indexing_status", "detected_file_type", "file_type"],
        }),
        ("Document status", {
            "fields": ["approved"],
        }),
    ]

    class Media:
        css = {
            'all': ('css/admin/custom_admin.css',)
        }
    # TODO: use presigned URL to upload to S3 directly, bypassing API Gateway restrictions
    # Easy to follow how to: https://www.hacksoft.io/blog/direct-to-s3-file-upload-with-django
    # Most of these methods will be rewritten then.

    def get_upload_link(self, key):
        s3_client = establish_client('s3')
        return s3_client.generate_presigned_post(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=key,
            ExpiresIn=20,
        )

    def save_model(self, request, obj, form, change):
        path = form.cleaned_data.get("file_upload")
        if path:
            obj.file_name = path._name
            self.upload_file(path, obj)
        super().save_model(request, obj, form, change)

    def upload_file(self, file, obj):
        result = self.get_upload_link(obj.key)
        requests.post(result['url'], data=result['fields'], files={'file': file}, timeout=200)

    def del_file(self, obj):
        s3_client = establish_client("s3")
        s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=obj.key)

    def delete_model(self, request, obj):
        try:
            self.del_file(obj)
            obj.delete()
        except Exception:
            raise Exception("Could not delete from server")

    def download_file(self, obj):
        if obj.id:
            link = reverse("file-download", kwargs={"file_id": obj.uid})
            return format_html(f"<input type=\"button\" onclick=\"location.href='{link}'\" value=\"Download File\" />")
        return "N/A"
