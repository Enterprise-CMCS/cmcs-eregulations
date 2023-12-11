from .base import * # noqa
import os
import socket
import re

DEBUG = os.environ.get("DEBUG", False)

# turns on django toolbar if debug is true
if DEBUG:
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[:-1] + '1' for ip in ips] + ['127.0.0.1', '10.0.2.2']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': os.environ.get('DB_USER', 'eregs'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'sgere'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'NAME': os.environ.get('DB_NAME', 'eregs'),
    },
    'postgres': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': os.environ.get('DB_USER', 'eregs'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'sgere'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'NAME': "postgres",
    },
}

AUTHENTICATION_BACKENDS = (
    'regulations.admin.OidcAdminAuthenticationBackend',
    'mozilla_django_oidc.auth.OIDCAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
)

S3_AWS_ACCESS_KEY_ID = os.environ.get("FILE_MANAGER_AWS_ACCESS_KEY_ID", None)
S3_AWS_SECRET_ACCESS_KEY = os.environ.get("FILE_MANAGER_AWS_SECRET_ACCESS_KEY", None)
AWS_STORAGE_BUCKET_NAME = os.environ.get("FILE_MANAGER_AWS_BUCKET_NAME", None)
AWS_S3_REGION_NAME = "us-east-1"
AWS_S3_CUSTOM_DOMAIN = (
    f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"
)
AWS_QUERYSTRING_AUTH = False
MEDIA_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
USE_AWS_TOKEN = True
TEXTRACT_KEY_ID = os.environ.get("TEXTRACT_KEY_ID", None)
TEXTRACT_SECRET_KEY = os.environ.get("TEXTRACT_SECRET_KEY", None)
USE_LOCAL_TEXTRACT = True
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
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/'
EUA_FEATUREFLAG = os.getenv('EUA_FEATUREFLAG', 'False').lower() == 'true'

if re.match(r'^dev\d*$', STAGE_ENV) or STAGE_ENV == 'dev' or STAGE_ENV == 'val':
    LOGIN_REDIRECT_URL = f"/{STAGE_ENV}/admin/"
    LOGOUT_REDIRECT_URL = f"/{STAGE_ENV}/"
