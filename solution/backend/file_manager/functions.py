
from django.conf import settings

from common.functions import establish_client


def get_upload_link(key):
    s3_client = establish_client('s3')

    try:
        result = s3_client.generate_presigned_post(Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                                                   Key=key,
                                                   ExpiresIn=20)
    except Exception as e:
        return e
    return result
