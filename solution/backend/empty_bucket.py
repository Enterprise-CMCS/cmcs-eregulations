import os

import boto3


def delete_versions(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.object_versions.delete()


def empty_bucket(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.objects.all().delete()


def handler(event, context):
    stage = os.environ.get("STAGE_ENV")
    storage_bucket_name = os.environ.get("AWS_STORAGE_BUCKET_NAME", None)

    if not stage:
        raise ValueError("Missing environment variable: STAGE_ENV")

    if not storage_bucket_name:
        raise ValueError("Missing environment variable: AWS_STORAGE_BUCKET_NAME")

    # Dynamically construct the CloudFront logs bucket name based on the stage
    cloudfront_logs_bucket_name = f"eregs-{stage}-cloudfront-logs"

    # Empty the specified storage bucket without deleting versions
    empty_bucket(storage_bucket_name)

    # Empty the CloudFront logs bucket and delete all versions and markers
    empty_bucket(cloudfront_logs_bucket_name)
    delete_versions(cloudfront_logs_bucket_name)

    return {
        "message": f"Emptied {storage_bucket_name} and processed versions in {cloudfront_logs_bucket_name}"
    }
