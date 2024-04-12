import os

import boto3
from botocore.exceptions import ClientError


def delete_all_object_versions(bucket_name):
    """
    Deletes all versions of all objects in a versioned bucket.
    :param bucket_name: The name of the bucket.
    """
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    try:
        bucket.object_versions.delete()
        print(f"Permanently deleted all object versions in bucket {bucket_name}.")
    except ClientError as e:
        print(f"Couldn't delete objects in bucket {bucket_name}: {e}")


def empty_bucket(bucket_name):
    """
    Empties the S3 bucket specified by bucket_name.
    """
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    try:
        bucket.objects.all().delete()
        print(f"Emptied bucket {bucket_name}.")
    except ClientError as e:
        print(f"Could not empty bucket {bucket_name}: {e}")


def handler(event, context):
    stage = os.environ.get("STAGE_ENV")
    storage_bucket_name = os.environ.get("AWS_STORAGE_BUCKET_NAME")
    cloudfront_logs_bucket_name = f"eregs-{stage}-cloudfront-logs"

    if not stage or not storage_bucket_name:
        print("Missing required environment variable: STAGE_ENV or AWS_STORAGE_BUCKET_NAME")
        return {"message": "Error: Missing required environment variables."}

    # Empty file storage bucket
    empty_bucket(storage_bucket_name)

    # Empty the versioned CloudFront logs bucket and delete all versions
    delete_all_object_versions(cloudfront_logs_bucket_name)
    empty_bucket(cloudfront_logs_bucket_name)

    return {
        "message": f"Successfully emptied {storage_bucket_name} and {cloudfront_logs_bucket_name}."
    }
