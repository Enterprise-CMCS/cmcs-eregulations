
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class PublicMediaStorage(S3Boto3Storage):
    access_key = settings.S3_AWS_ACCESS_KEY_ID
    secret_key = settings.S3_AWS_SECRET_ACCESS_KEY
