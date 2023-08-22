import boto3
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.html import format_html

from .models import UploadedFile


class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('file_link', 'created_at')
    search_fields = ('file__name', 'created_at')

    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.file.url, obj.file.name)
        return None
    file_link.short_description = 'File'  # Customize the column header

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('upload_files/', self.upload_files_view, name='upload_files'),
        ]
        return my_urls + urls

    def delete_model(self, request, obj):
        if settings.S3_AWS_ACCESS_KEY_ID and settings.S3_AWS_SECRET_ACCESS_KEY:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.S3_AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.S3_AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )
            bucket_name = settings.S3_AWS_STORAGE_BUCKET_NAME
            print(f"---Deleting S3 object: {obj.file.name}")
            try:
                s3_client.delete_object(Bucket=bucket_name, Key=obj.file.name)
            except Exception as e:
                print("Error deleting S3 object:", str(e))

        obj.delete()

    def upload_files_view(self, request):
        if request.method == 'POST':
            files = request.FILES.getlist('file')
            if settings.S3_AWS_ACCESS_KEY_ID and settings.S3_AWS_SECRET_ACCESS_KEY:
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.S3_AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.S3_AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME,
                )
                bucket_name = settings.S3_AWS_STORAGE_BUCKET_NAME
                for file in files:
                    file_key = file.name
                    s3_client.upload_fileobj(file, bucket_name, file_key)

                return HttpResponseRedirect(reverse('admin:file_manager_uploadedfile_changelist'))

            else:
                # Handle the case when AWS keys are not provided (you might want to display an error message)
                pass

        context = self.admin_site.each_context(request)
        return render(request, 'admin/file_manager/upload_files.html', context)


admin.site.register(UploadedFile, UploadedFileAdmin)
