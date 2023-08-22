from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView


class PolicyRepositoryView(LoginRequiredMixin, TemplateView):
    login_url = "/admin/login/?next=/policy-repository/"
    template_name = 'regulations/policy_repository.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        host = self.request.get_host()

        c = {
            'host': host
        }

        return {**context, **c}
