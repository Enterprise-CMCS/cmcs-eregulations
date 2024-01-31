from django.views.generic.base import TemplateView


class LoginView(TemplateView):

    template_name = 'regulations/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', '')
        return context

