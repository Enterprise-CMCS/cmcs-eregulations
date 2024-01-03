from .base import * # noqa
import os
import re

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

AUTHENTICATION_BACKENDS = (
    'regulations.admin.OidcAdminAuthenticationBackend',
    'mozilla_django_oidc.auth.OIDCAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
)

STAGE_ENV = os.environ.get("STAGE_ENV", "")
BASE_URL = os.environ.get("BASE_URL", "")

# EUA settings
OIDC_RP_IDP_SIGN_KEY = os.environ.get("OIDC_RP_IDP_SIGN_KEY", None)
OIDC_RP_CLIENT_ID = os.environ.get("OIDC_RP_CLIENT_ID", None)
OIDC_RP_CLIENT_SECRET = os.environ.get("OIDC_RP_CLIENT_SECRET", None)
OIDC_OP_AUTHORIZATION_ENDPOINT = os.environ.get("OIDC_OP_AUTHORIZATION_ENDPOINT", None)
OIDC_OP_TOKEN_ENDPOINT = os.environ.get("OIDC_OP_TOKEN_ENDPOINT", None)
OIDC_OP_USER_ENDPOINT = os.environ.get("OIDC_OP_USER_ENDPOINT", None)
OIDC_OP_JWKS_ENDPOINT = os.environ.get("OIDC_OP_JWKS_ENDPOINT", None)
OIDC_REDIRECT_URL = "/admin/oidc/callback/"
OIDC_RP_SIGN_ALGO = 'RS256'
OIDC_END_EUA_SESSION = os.environ.get("OIDC_END_EUA_SESSION", None)
OIDC_OP_LOGOUT_URL_METHOD = 'regulations.logout.eua_logout'
OIDC_STORE_ID_TOKEN = True
LOGIN_REDIRECT_URL = '/admin/'
EUA_FEATUREFLAG = os.getenv('EUA_FEATUREFLAG', 'False').lower() == 'true'

if re.match(r'^dev\d*$', STAGE_ENV) or STAGE_ENV == 'dev' or STAGE_ENV == 'val':
    LOGIN_REDIRECT_URL = f"/{STAGE_ENV}/admin/"
