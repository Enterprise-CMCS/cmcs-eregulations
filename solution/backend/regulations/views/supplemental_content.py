from django.views.generic.base import TemplateView
from django.http import Http404

from supplemental_content.models import TempSupplementalContent


class SupplementalContentView(TemplateView):

    template_name = "regulations/supplemental_content.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content_id = self.kwargs.get("id")
        content = SupplementalContent.objects.filter(id=content_id, approved=True)
        if len(content) < 1:
            raise Http404
        content = content[0]
        c = {
            "title": content.name,
            "description": content.description,
            "pub_time": content.date,
            "mod_time": content.updated_at.isoformat(),
            "redirect_link": content.url,
        }
        return {**context, **c}
