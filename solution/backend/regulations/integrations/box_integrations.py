from django.conf import settings
from boxsdk import OAuth2


def get_authorization_url():
    """
    Get the authorization url for the user
    """

    oauth = OAuth2(
        client_id=settings.BOX_CLIENT_ID,
        client_secret=settings.BOX_CLIENT_SECRET,
    )
    auth_url, csrf_token = oauth.get_authorization_url(settings.BOX_REDIRECT_URL)
    print(f"auth_url is {auth_url}")
    return auth_url, csrf_token


def get_box_client(access_token=None):
    oauth = OAuth2(
        client_id=settings.BOX_CLIENT_ID,
        client_secret=settings.BOX_CLIENT_SECRET,
        store_tokens=store_tokens_callback
    )

    if access_token:
        oauth.authenticate(access_token=access_token)
    else:
        # Redirect the user to the authorization URL
        auth_url, csrf_token = oauth.get_authorization_url(settings.BOX_REDIRECT_URL)
        # Store the csrf_token in the session for validation later

        return auth_url


def store_tokens_callback(access_token, refresh_token):
    # Implement your logic to store the tokens
    # You might want to store them in a secure storage (e.g., database)

    # Example code for demonstration purposes only
    # Replace with your own logic
    print("Access Token:", access_token)
    print("Refresh Token:", refresh_token)
