
import boto3
from django.conf import settings


def establish_client():
    if settings.DEBUG:
        return boto3.client('s3',
                            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    else:
        return boto3.client('s3', config=boto3.session.Config(signature_version='s3v4',))
