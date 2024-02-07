from django.views.generic.base import TemplateView


class PolicyRepositoryView(TemplateView):

    template_name = 'regulations/policy_repository.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        host = self.request.get_host()
        is_authenticated = self.request.user.is_authenticated
        user_groups = [group.name for group in self.request.user.groups.all()]
        has_editable_job_code = any(group in ['EREGS_ADMIN', 'EREGS_MANAGER', 'EREGS_EDITOR'] for group in user_groups)

        c = {
            'host': host,
            'is_authenticated': is_authenticated,
            'has_editable_job_code': has_editable_job_code,
        }

        return {**context, **c}
