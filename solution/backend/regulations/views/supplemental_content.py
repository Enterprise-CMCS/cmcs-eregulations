from django.http import Http404
from django.urls import reverse
from django.views.generic.base import TemplateView

from resources.models import AbstractResource


class SupplementalContentView(TemplateView):

    template_name = "regulations/supplemental_content.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content_id = self.kwargs.get("id")
        try:
            content = AbstractResource.objects.all().select_subclasses().get(id=content_id, approved=True)
            c = {
                "mod_time": content.updated_at.isoformat(),
                "title": getattr(content, "name", "n/a"),
                "description": getattr(content, "description", "n/a"),
                "pub_time": getattr(content, "date", "n/a"),
                "redirect_link": getattr(content, "url", reverse("homepage")),
            }
            return {**context, **c}
        except AbstractResource.DoesNotExist:
            raise Http404
