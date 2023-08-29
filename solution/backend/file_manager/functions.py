
import boto3
from django.conf import settings


def establish_client():
    if settings.DEBUG:
        return boto3.client('s3',
                            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    else:
        return boto3.client('s3', config=boto3.session.Config(signature_version='s3v4',))


def generate_download_link(obj):
    s3_client = establish_client()
    try:
        return s3_client.generate_presigned_url('get_object',
                                                Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                        'Key': obj.file.name},
                                                ExpiresIn=600)
    except Exception:
        print('Could not set up download url.')
        return 'Not available for download.'
