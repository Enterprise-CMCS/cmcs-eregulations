from django.conf import settings
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework import authentication, exceptions


class SettingsAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'common.auth.SettingsAuthentication'
    name = 'SettingsAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer'
        }


class SettingsUser:
    is_authenticated = False


class SettingsAuthentication(authentication.BasicAuthentication):
    def authenticate_credentials(self, userid, password, request=None):
        if userid == settings.HTTP_AUTH_USER and password == settings.HTTP_AUTH_PASSWORD:
            user = SettingsUser()
            user.is_authenticated = True
            return (user, None)
        raise exceptions.AuthenticationFailed('No such user')
