from django.views.generic.base import TemplateView

from regulations.views.mixins import IsAuthenticatedMixin


class PolicyRepositoryView(IsAuthenticatedMixin, TemplateView):

    template_name = 'regulations/policy_repository.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        host = self.request.get_host()

        c = {
            'host': host
        }

        return {**context, **c}
