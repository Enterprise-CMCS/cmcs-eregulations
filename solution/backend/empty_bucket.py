import os

import boto3

def empty_bucket(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.objects.all().delete()


def handler(event, context):
    stage = os.environ.get("STAGE_ENV")

    # empty storage bucket
    empty_bucket(os.environ.get("AWS_STORAGE_BUCKET_NAME", None))

    # empty the cloudfront logs bucket.
    empty_bucket(f"eregs-{stage}-cloudfront-logs")
