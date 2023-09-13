from .deploy import * # noqa
import os
import re

INSTALLED_APPS += [ # noqa
    'mozilla_django_oidc',
]

OIDC_RP_IDP_SIGN_KEY = os.environ.get("OIDC_RP_IDP_SIGN_KEY", None)

AUTHENTICATION_BACKENDS = (
    'mozilla_django_oidc.auth.OIDCAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
    'regulations.admin.OidcAdminAuthenticationBackend',
)

STAGE_ENV = os.environ.get("STAGE_ENV", "")
BASE_URL = os.environ.get("BASE_URL", "")
OIDC_RP_CLIENT_ID = os.environ.get("OIDC_RP_CLIENT_ID", None)
OIDC_RP_CLIENT_SECRET = os.environ.get("OIDC_RP_CLIENT_SECRET", None)
OIDC_OP_AUTHORIZATION_ENDPOINT = os.environ.get("OIDC_OP_AUTHORIZATION_ENDPOINT", None)
OIDC_OP_TOKEN_ENDPOINT = os.environ.get("OIDC_OP_TOKEN_ENDPOINT", None)
OIDC_OP_USER_ENDPOINT = os.environ.get("OIDC_OP_USER_ENDPOINT", None)
OIDC_OP_JWKS_ENDPOINT = os.environ.get("OIDC_OP_JWKS_ENDPOINT", None)
OIDC_RP_SIGN_ALGO = 'RS256'
EUA_FEATUREFLAG = os.environ.get('EUA_FEATUREFLAG', 'false')
BASE_PATH = ""
if re.match(r'^dev\d*$', STAGE_ENV):
    numeric_part = re.sub(r'^dev', '', STAGE_ENV)
    BASE_PATH = BASE_URL.replace('/dev', f'/{numeric_part}')
else:
    BASE_PATH = BASE_URL
LOGIN_REDIRECT_URL = BASE_PATH + '/admin/'
LOGOUT_REDIRECT_URL = BASE_PATH + '/'
