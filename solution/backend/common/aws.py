import boto3
from django.conf import settings


# Establishes an AWS client.
#
# client_type: the boto3-recognized AWS resource to create a client for.
def establish_client(client_type):
    if settings.USE_AWS_TOKEN:
        return boto3.client(
            client_type,
            aws_access_key_id=settings.S3_AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_AWS_SECRET_ACCESS_KEY,
            region_name="us-east-1",
        )
    else:
        return boto3.client(client_type, region_name="us-east-1")
