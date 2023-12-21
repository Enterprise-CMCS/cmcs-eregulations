from mozilla_django_oidc.views import OIDCLogoutView


class LogoutView(OIDCLogoutView):
    def get(self, request):
        return self.post(request)
