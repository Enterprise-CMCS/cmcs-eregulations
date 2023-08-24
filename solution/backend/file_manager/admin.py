import boto3
from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

from .models import UploadedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ("name", 'delete')
    search_fields = ["name"]
    ordering = ("name",)
    fields = ("name", "file",)

    change_form_template = "admin/edit_file.html"

    def download(self, obj):
        s3_client = boto3.client('s3',
                                 aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                 aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        try:
            response = s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                                'Key': obj.file.name},
                                                        ExpiresIn=600)
        except Exception as e:
            print(e)
        return response

    def delete(self, obj):
        link = self.download(obj)
        html = '<input type="button" onclick="location.href=\'{}\'" value="download" />'.format(link)
        return format_html(html)
