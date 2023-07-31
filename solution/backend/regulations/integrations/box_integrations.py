from django.conf import settings
from boxsdk import OAuth2


def get_oauth():
    return OAuth2(
        client_id=settings.BOX_CLIENT_ID,
        client_secret=settings.BOX_CLIENT_SECRET,
    )


def get_authorization_url():
    oauth = get_oauth()
    auth_url, csrf_token = oauth.get_authorization_url(settings.BOX_REDIRECT_URL)

    return auth_url, csrf_token
