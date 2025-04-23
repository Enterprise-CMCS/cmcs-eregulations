from .base import * # noqa
import os

from secret_manager import get_username, get_password


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
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

SERVER_USER = os.environ.get("SERVER_USER", '')
SERVER_PASSWORD = os.environ.get("SERVER_PASSWORD", '')
# TODO - this should be removed after we merge euasettings.py with base.py in teh future

BASE_URL = os.environ.get("BASE_URL", "")
from .euasettings import * # noqa

OIDC_OP_JWKS_ENDPOINT = "/example/jwks/endpoint/"
OIDC_REDIRECT_URL = "/admin/oidc/callback/"
OIDC_RP_SIGN_ALGO = 'RS256'
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/logout'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': get_username("DB_SECRET", environment_fallback="DB_USER", default="eregsuser"),
        'PASSWORD': get_password("DB_SECRET", environment_fallback="DB_PASSWORD", default="sgere"),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'NAME': os.environ.get('DB_NAME', 'eregs'),
    },
}
