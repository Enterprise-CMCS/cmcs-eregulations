from .base import * # noqa
import os

USE_AWS_TOKEN = True
S3_AWS_ACCESS_KEY_ID = os.environ.get("FILE_MANAGER_AWS_ACCESS_KEY_ID", 'test')
S3_AWS_SECRET_ACCESS_KEY = os.environ.get("FILE_MANAGER_AWS_SECRET_ACCESS_KEY", 'test')
AWS_STORAGE_BUCKET_NAME = 'test_bucket'
AWS_S3_REGION_NAME = "us-east-1"
AWS_S3_CUSTOM_DOMAIN = (
    f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"
)
AWS_QUERYSTRING_AUTH = False
MEDIA_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

SERVER_USER = os.environ.get("SERVER_USER", '')
SERVER_PASSWORD = os.environ.get("SERVER_PASSWORD", '')
# TODO - this should be removed after we merge euasettings.py with base.py in teh future

BASE_URL = os.environ.get("BASE_URL", "")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': os.environ.get('DB_USER', 'eregs'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'sgere'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'NAME': os.environ.get('DB_NAME', 'eregs'),
    },
}

# EUA settings
from .euasettings import * # noqa
