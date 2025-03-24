import os

from secret_manager import get_password, get_username

# EUA settings
AUTHENTICATION_BACKENDS = (
    'regulations.admin.OidcAdminAuthenticationBackend',
    'mozilla_django_oidc.auth.OIDCAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
)

STAGE_ENV = os.environ.get("STAGE_ENV", "")
OIDC_RP_IDP_SIGN_KEY = os.environ.get("OIDC_RP_IDP_SIGN_KEY", None)
OIDC_RP_CLIENT_ID = get_username("OIDC_RP_CLIENT_SECRET", environment_fallback="OIDC_RP_CLIENT_ID")
OIDC_RP_CLIENT_SECRET = get_password("OIDC_RP_CLIENT_SECRET", environment_fallback="OIDC_RP_CLIENT_SECRET")
OIDC_OP_AUTHORIZATION_ENDPOINT = os.environ.get("OIDC_OP_AUTHORIZATION_ENDPOINT", None)
OIDC_OP_TOKEN_ENDPOINT = os.environ.get("OIDC_OP_TOKEN_ENDPOINT", None)
OIDC_OP_USER_ENDPOINT = os.environ.get("OIDC_OP_USER_ENDPOINT", None)
OIDC_OP_JWKS_ENDPOINT = os.environ.get("OIDC_OP_JWKS_ENDPOINT", None)
OIDC_REDIRECT_URL = '/admin/oidc/callback/'
OIDC_RP_SIGN_ALGO = 'RS256'
LOGIN_REDIRECT_URL = 'custom_login'
LOGOUT_REDIRECT_URL = 'logout'
EUA_FEATUREFLAG = os.getenv('EUA_FEATUREFLAG', 'False').lower() == 'true'
OIDC_END_EUA_SESSION = os.environ.get("OIDC_END_EUA_SESSION", None)
OIDC_OP_LOGOUT_URL_METHOD = 'regulations.logout.eua_logout'
OIDC_STORE_ID_TOKEN = True
