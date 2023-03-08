from rest_framework import authentication
from rest_framework import exceptions


class SettingsUser:  # TODO: keep this on v3 move
    is_authenticated = False


class SettingsAuthentication(authentication.BasicAuthentication):  # TODO: keep this on v3 move
    def authenticate_credentials(self, userid, password, request=None):
        if userid == settings.HTTP_AUTH_USER and password == settings.HTTP_AUTH_PASSWORD:
            user = SettingsUser()
            user.is_authenticated = True
            return (user, None)
        raise exceptions.AuthenticationFailed('No such user')
