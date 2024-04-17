import os

import boto3


def empty_bucket(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.objects.all().delete()


def handler(event, context):
    stage = os.environ.get("STAGE_ENV")
    storage_bucket_name = os.environ.get("AWS_STORAGE_BUCKET_NAME")
    cloudfront_logs_bucket_name = f"eregs-{stage}-cloudfront-logs"

    # empty storage bucket
    empty_bucket(storage_bucket_name)

    # empty the cloudfront logs bucket.
    empty_bucket(cloudfront_logs_bucket_name)
