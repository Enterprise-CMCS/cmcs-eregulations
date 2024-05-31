from django.views.generic.base import TemplateView

from resources.models import NewSubject


class SubjectsView(TemplateView):

    template_name = 'regulations/subjects.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject_id = self.request.GET.get('subjects')

        try:
            subject = NewSubject.objects.get(id=subject_id)
            subject_abbreviation = subject.abbreviation
            subject_fullname = subject.full_name
            subject_name = subject_abbreviation if subject_abbreviation else subject_fullname
        except (ValueError, NewSubject.DoesNotExist):
            subject_name = None

        host = self.request.get_host()
        is_authenticated = self.request.user.is_authenticated
        user_groups = [group.name for group in self.request.user.groups.all()]
        has_editable_job_code = any(group in ['EREGS_ADMIN', 'EREGS_MANAGER', 'EREGS_EDITOR'] for group in user_groups)

        c = {
            'host': host,
            'is_authenticated': is_authenticated,
            'has_editable_job_code': has_editable_job_code,
            'subject_name': subject_name
        }

        return {**context, **c}
