from django.contrib import admin
from django.http.request import HttpRequest
from django.http.response import HttpResponse
import boto3
from .models import UploadedFile
from django.conf import settings

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    
    list_display = ("name",)
    search_fields = ["name"]
    ordering = ("name",)
    fields = ("name", "file",)


    change_form_template = "admin/edit_file.html"
    def response_change(self, request, obj):
        if "download-file" in request.POST:
            s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
            s3.download_file(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Filename=obj.file.name.split('/')[1], Key=obj.file.name)

