from .deploy import * # noqa
import os

INSTALLED_APPS += [ # noqa
    'mozilla_django_oidc',
]

OIDC_RP_IDP_SIGN_KEY = os.environ.get("OIDC_RP_IDP_SIGN_KEY", None)

AUTHENTICATION_BACKENDS = (
    'mozilla_django_oidc.auth.OIDCAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
    'regulations.admin.OidcAdminAuthenticationBackend',
)
OIDC_RP_CLIENT_ID = os.environ.get("OIDC_RP_CLIENT_ID", None)
OIDC_RP_CLIENT_SECRET = os.environ.get("OIDC_RP_CLIENT_SECRET", None)
OIDC_OP_AUTHORIZATION_ENDPOINT = os.environ.get("OIDC_OP_AUTHORIZATION_ENDPOINT", None)
OIDC_OP_TOKEN_ENDPOINT = os.environ.get("OIDC_OP_TOKEN_ENDPOINT", None)
OIDC_OP_USER_ENDPOINT = os.environ.get("OIDC_OP_USER_ENDPOINT", None)
OIDC_OP_JWKS_ENDPOINT = os.environ.get("OIDC_OP_JWKS_ENDPOINT", None)
OIDC_RP_SIGN_ALGO = 'RS256'
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/'
EUA_FEATUREFLAG = os.environ.get('EUA_FEATUREFLAG', 'false')
