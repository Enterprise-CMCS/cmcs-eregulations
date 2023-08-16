
import boto3
from django.conf import settings
from django.shortcuts import render


def file_manager(request):
    uploaded_files = []

    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

        response = s3_client.list_objects(Bucket=bucket_name)
        if 'Contents' in response:
            for item in response['Contents']:
                uploaded_files.append(item['Key'])
    else:
        return render(request, 'file_manager.html', {'uploaded_files': uploaded_files})
