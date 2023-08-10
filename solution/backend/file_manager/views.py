import boto3
import uuid
from django.shortcuts import render
from django.utils import timezone
from django.conf import settings

from .models import UploadedFile


def file_manager(request):
    if settings.AWS_OIDC_ROLE_TO_ASSUME:
        # Assume IAM role using AWS_OIDC_ROLE_TO_ASSUME and obtain temporary credentials
        sts_client = boto3.client('sts')
        assumed_role = sts_client.assume_role(
            RoleArn=settings.AWS_OIDC_ROLE_TO_ASSUME,
            RoleSessionName='file-upload-session'
        )
        credentials = assumed_role['Credentials']
        s3_client = boto3.client(
            's3',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )
    else:
        # Use AWS access keys for local development
        aws_access_key_id = settings.AWS_ACCESS_KEY_ID
        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
    if request.method == 'POST':
        file = request.FILES['file']
        # Generate a unique key for the uploaded file (e.g., using UUID)
        file_key = str(uuid.uuid4())

        # Upload the file to S3
        s3_client.upload_fileobj(file, settings.AWS_STORAGE_BUCKET_NAME, file_key)

        # Save the uploaded file information to the database
        UploadedFile.objects.create(file=file, created_at=timezone.now())

    uploaded_files = UploadedFile.objects.all()
    return render(request, 'file_manager.html', {'uploaded_files': uploaded_files})
