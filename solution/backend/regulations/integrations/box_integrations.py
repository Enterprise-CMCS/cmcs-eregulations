from django.conf import settings
from boxsdk import OAuth2


def get_oauth(store_tokens=None):
    return OAuth2(
        client_id=settings.BOX_CLIENT_ID,
        client_secret=settings.BOX_CLIENT_SECRET,
        store_tokens=store_tokens,
    )


def get_authorization_url():
    oauth = get_oauth()
    auth_url, csrf_token = oauth.get_authorization_url(settings.BOX_REDIRECT_URL)

    return auth_url, csrf_token


def store_tokens(access_token, refresh_token):
    # Store the tokens in a database or a file
    pass