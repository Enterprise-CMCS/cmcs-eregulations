import os

import boto3


def handler(event, context):
    bucket_name = os.environ.get("AWS_STORAGE_BUCKET_NAME", None)
    s3 = boto3.resource('s3')
    bucket = s3.bucket(bucket_name)
    bucket.objects.all().delete()
