from django.views.generic.base import TemplateView

from regulations.views.mixins import IsAuthenticatedMixin


class PolicyRepositoryView(IsAuthenticatedMixin, TemplateView):

    template_name = 'regulations/policy_repository.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        host = self.request.get_host()
        is_authenticated = self.request.user.is_authenticated
        user_groups = [group.name for group in self.request.user.groups.all()]
        has_editable_job_code = user_groups and user_groups != ['EREGS_EDITOR']


        c = {
            'host': host,
            'is_authenticated': is_authenticated,
            'has_editable_job_code': has_editable_job_code,
        }

        return {**context, **c}
