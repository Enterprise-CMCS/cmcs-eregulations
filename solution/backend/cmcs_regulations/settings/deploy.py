from .base import * # noqa
import os

default_database_values = {
    'ENGINE': 'django.db.backends.postgresql',
    'USER': os.environ.get('DB_USER', 'eregs'),
    'PORT': os.environ.get('DB_PORT', '5432'),
    'HOST': os.environ.get('DB_HOST', 'db'),
    'PASSWORD': os.environ.get('DB_PASSWORD', 'sgere'),
}

DATABASES = {
    'default': {
        **default_database_values,
        'NAME': os.environ.get('DB_NAME', 'eregs'),
    },
    'postgres': {
        **default_database_values,
        'NAME': "postgres",
    },
}
OIDC_RP_IDP_SIGN_KEY = os.environ.get("OIDC_RP_IDP_SIGN_KEY", None)
S3_AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", None)
S3_AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", None)
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME", None)
AWS_S3_REGION_NAME = "us-east-1"
AWS_S3_CUSTOM_DOMAIN = (
    f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"
)
AWS_QUERYSTRING_AUTH = False
MEDIA_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
USE_AWS_TOKEN = False
BASE_URL = os.environ.get("BASE_URL", "")

# EUA settings
from .euasettings import * # noqa