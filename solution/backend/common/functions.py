import boto3
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


# Returns an empty string if none instead of "None"
def check_string_value(check_string):
    return check_string if check_string else ''


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def establish_client(client_type):
    if settings.USE_AWS_TOKEN:
        return boto3.client(client_type,
                            aws_access_key_id=settings.S3_AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=settings.S3_AWS_SECRET_ACCESS_KEY,
                            region_name="us-east-1")
    else:
        return boto3.client(client_type, region_name="us-east-1")
