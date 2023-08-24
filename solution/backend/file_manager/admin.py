import os

import boto3
from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

from .models import UploadedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ("name", 'download_file')
    search_fields = ["name"]
    ordering = ("name",)
    fields = ("name", "file",)

    def download(self, obj):
        s3_client = boto3.client('s3',
                                 aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                                 aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
                                 aws_session_token=os.environ["AWS_ACCESS_KEY_ID"])
        try:
            response = s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                                'Key': obj.file.name},
                                                        ExpiresIn=600)
        except Exception as e:
            print(e)
        return response

    def download_file(self, obj):
        link = self.download(obj)
        html = '<input type="button" onclick="location.href=\'{}\'" value="download" />'.format(link)
        return format_html(html)
