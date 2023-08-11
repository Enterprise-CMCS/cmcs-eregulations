import uuid

import boto3
from django.conf import settings
from django.shortcuts import render
from django.utils import timezone

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
        uploaded_files = UploadedFile.objects.all()
        return render(request, 'file_manager.html', {'uploaded_files': uploaded_files})
