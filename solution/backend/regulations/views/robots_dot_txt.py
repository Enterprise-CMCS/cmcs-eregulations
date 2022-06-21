from django.views.generic.base import TemplateView

from regulations.models import SiteConfiguration


class RobotsDotTxtView(TemplateView):

    template_name = "robots.txt"
    content_type = "text/plain"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allow"] = SiteConfiguration.objects.first().allow_indexing
        return context
