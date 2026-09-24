from django.contrib.auth.views import LoginView as DjangoLoginView
from django.http import HttpResponseNotFound
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic.base import TemplateView

from regulations.admin_login import is_admin_login_enabled


class LoginView(TemplateView):

    template_name = 'regulations/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', '')
        return context


@method_decorator(never_cache, name="dispatch")
class AdminLoginView(DjangoLoginView):
    """Expose Django credential login only for approved outage or Cypress requests."""

    template_name = "admin/login.html"

    def dispatch(self, request, *args, **kwargs):
        if not is_admin_login_enabled(request):
            return HttpResponseNotFound()
        return super().dispatch(request, *args, **kwargs)
