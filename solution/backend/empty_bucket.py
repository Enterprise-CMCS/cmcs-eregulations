import os
import boto3


def empty_bucket(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    # Delete all objects in the bucket
    bucket.objects.all().delete()

    # Handle versioned buckets
    bucket_versioning = s3.BucketVersioning(bucket_name)
    if bucket_versioning.status == 'Enabled':
        # Delete all object versions and delete markers
        bucket.object_versions.delete()


def handler(event, context):
    # Retrieve the stage/environment variable
    stage = os.environ.get("STAGE")

    storage_bucket_name = os.environ.get("AWS_STORAGE_BUCKET_NAME", None)

    if not stage:
        raise ValueError("Missing environment variable: STAGE")

    if not storage_bucket_name:
        raise ValueError("Missing environment variable: AWS_STORAGE_BUCKET_NAME")

    # Dynamically construct the CloudFront logs bucket name based on the stage
    cloudfront_logs_bucket_name = f"eregs-{stage}-cloudfront-logs"

    # Empty the specified storage bucket
    empty_bucket(storage_bucket_name)

    # Empty the dynamically named CloudFront logs bucket
    empty_bucket(cloudfront_logs_bucket_name)

    return {
        "message": f"Emptied {storage_bucket_name} and {cloudfront_logs_bucket_name}"
    }
