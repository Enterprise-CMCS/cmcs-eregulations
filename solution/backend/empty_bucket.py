import os

import boto3
from botocore.exceptions import ClientError


def delete_all_object_versions(bucket_name):
    print(f"Emptying bucket {bucket_name}")

    s3_client = boto3.client('s3')
    paginator = s3_client.get_paginator('list_object_versions')

    # Initialize deletion list
    deletion_list = {'Objects': []}

    # Paginate through list of object versions
    for page in paginator.paginate(Bucket=bucket_name):
        if 'Versions' in page:
            for version in page['Versions']:
                deletion_list['Objects'].append({'Key': version['Key'], 'VersionId': version['VersionId']})
        if 'DeleteMarkers' in page:
            for marker in page['DeleteMarkers']:
                deletion_list['Objects'].append({'Key': marker['Key'], 'VersionId': marker['VersionId']})

    # Delete if there are objects to delete
    if deletion_list['Objects']:
        response = s3_client.delete_objects(Bucket=bucket_name, Delete=deletion_list)
        print(f"Deleted versions and markers from bucket {bucket_name}: {response}")

    # As a safety measure, try to remove any remaining objects
    # Note: This might not be necessary after the above deletions, but it's kept for completeness
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    while response.get('Contents', []):
        s3_client.delete_objects(
            Bucket=bucket_name,
            Delete={'Objects': [{'Key': obj['Key']} for obj in response['Contents']]})
        response = s3_client.list_objects_v2(Bucket=bucket_name)

    print(f"Bucket {bucket_name} should now be empty.")


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

    if not stage or not storage_bucket_name:
        print("Missing required environment variable: STAGE_ENV or AWS_STORAGE_BUCKET_NAME")
        return {"message": "Error: Missing required environment variables."}

    cloudfront_logs_bucket_name = f"eregs-{stage}-cloudfront-logs"

    # Directly empty the non-versioned storage bucket
    empty_bucket(storage_bucket_name)

    # Empty the versioned CloudFront logs bucket and delete all versions
    delete_all_object_versions(cloudfront_logs_bucket_name)
    empty_bucket(cloudfront_logs_bucket_name)

    return {
        "message": f"Successfully emptied {storage_bucket_name} and {cloudfront_logs_bucket_name}."
    }
