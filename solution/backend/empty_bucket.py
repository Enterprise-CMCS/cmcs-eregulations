import os

import boto3


def delete_versions_and_markers(bucket_name):
    s3 = boto3.client('s3')
    # Get all versions and delete markers
    versions = s3.list_object_versions(Bucket=bucket_name)
    delete_markers = versions.get('DeleteMarkers', [])
    versions = versions.get('Versions', [])

    # Prepare objects for deletion
    objects_to_delete = {'Objects': []}
    objects_to_delete['Objects'].extend([
        {'Key': version['Key'], 'VersionId': version['VersionId']} for version in versions
    ])
    objects_to_delete['Objects'].extend([
        {'Key': marker['Key'], 'VersionId': marker['VersionId']} for marker in delete_markers
    ])

    # Delete versions and delete markers if any
    if objects_to_delete['Objects']:
        s3.delete_objects(Bucket=bucket_name, Delete=objects_to_delete)


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
        raise ValueError("Missing environment variable: AWS_STORAGE_BUCKET_NAME", None)

    # Dynamically construct the CloudFront logs bucket name based on the stage
    cloudfront_logs_bucket_name = f"eregs-{stage}-cloudfront-logs"

    # Empty the specified storage bucket without deleting versions
    empty_bucket(storage_bucket_name)

    # Empty the CloudFront logs bucket and delete all versions and markers
    empty_bucket(cloudfront_logs_bucket_name)
    delete_versions_and_markers(cloudfront_logs_bucket_name)

    return {
        "message": f"Emptied {storage_bucket_name} and processed versions in {cloudfront_logs_bucket_name}"
    }
