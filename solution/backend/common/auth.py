from django.conf import settings
from rest_framework import authentication, exceptions


class SettingsUser:
    is_authenticated = False


class SettingsAuthentication(authentication.BasicAuthentication):
    def authenticate_credentials(self, userid, password, request=None):
        if userid == settings.HTTP_AUTH_USER and password == settings.HTTP_AUTH_PASSWORD:
            user = SettingsUser()
            user.is_authenticated = True
            return (user, None)
        raise exceptions.AuthenticationFailed('No such user')
