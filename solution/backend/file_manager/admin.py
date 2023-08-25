
import boto3
from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

from .models import UploadedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ["name"]
    ordering = ("name",)
    readonly_fields = ('download_file',)
    fields = ("name", "file", 'download_file')

    def download(self, obj):
        # for localized testing
        if settings.DEBUG:
            s3_client = boto3.client('s3',
                                     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        else:
            s3_client = boto3.client('s3', config=boto3.session.Config(signature_version='s3v4',))
        try:
            response = s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                                'Key': obj.file.name},
                                                        ExpiresIn=600)
        except Exception as e:
            print(e)
        return response

    def download_file(self, obj):
        if obj.id:
            link = self.download(obj)
            html = '<input type="button" onclick="location.href=\'{}\'" value="Download File" />'.format(link)
        else:
            return "N/A"
        return format_html(html)
