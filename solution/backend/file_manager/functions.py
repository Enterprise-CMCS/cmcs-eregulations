
import boto3
from django.conf import settings


def establish_client():
    if settings.USE_AWS_TOKEN:
        return boto3.client('s3',
                            aws_access_key_id=settings.S3_AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=settings.S3_AWS_SECRET_ACCESS_KEY)
    else:
        return boto3.client('s3', config=boto3.session.Config(signature_version='s3v4',))


def get_upload_link(key):
    s3_client = establish_client()

    try:
        result = s3_client.generate_presigned_post(Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                                                   Key=key,
                                                   ExpiresIn=20)
    except Exception as e:
        return e
    return result
