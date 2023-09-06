from .base import * # noqa
import os

INSTALLED_APPS += [ # noqa
    'mozilla_django_oidc',
]

OIDC_RP_IDP_SIGN_KEY = os.environ.get("OIDC_RP_IDP_SIGN_KEY", None)

AUTHENTICATION_BACKENDS = (
    'mozilla_django_oidc.auth.OIDCAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
)

OIDC_RP_CLIENT_ID = os.environ.get("OIDC_RP_CLIENT_ID", None)
OIDC_RP_CLIENT_SECRET = os.environ.get("OIDC_RP_CLIENT_SECRET", None)
OIDC_OP_AUTHORIZATION_ENDPOINT = os.environ.get("OIDC_OP_AUTHORIZATION_ENDPOINT", None)
OIDC_OP_TOKEN_ENDPOINT = os.environ.get("OIDC_OP_TOKEN_ENDPOINT", None)
OIDC_OP_USER_ENDPOINT = os.environ.get("OIDC_OP_USER_ENDPOINT", None)
OIDC_RP_SIGN_ALGO = 'RS256'
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/'
OIDC_OP_JWKS_ENDPOINT = 'https://test.idp.idm.cms.gov/oauth2/auski5g1bm92sixcI297/v1/keys'


default_database_values = {
    'ENGINE': 'django.db.backends.postgresql',
    'USER': os.environ.get('DB_USER', 'eregs'),
    'HOST': os.environ.get('DB_HOST', 'db'),
    'PORT': os.environ.get('DB_PORT', '5432'),
}

DATABASES = {
    'default': {
        **default_database_values,
        'PASSWORD': os.environ.get('DB_PASSWORD', 'sgere'),
        'NAME': os.environ.get('DB_NAME', 'eregs'),
    },
    'postgres': {
        **default_database_values,
        'PASSWORD': os.environ.get('DB_PASSWORD', 'sgere'),
        'NAME': "postgres",
    },
}

LOGIN_URL = 'localhost:8000/dev/oidc/callback'
LOGOUT_URL = '/auth/logout/'
