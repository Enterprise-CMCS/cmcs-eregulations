from django.views.generic.base import TemplateView
from django.http import Http404

from supplemental_content.models import SupplementalContent

class SupplementalContentView(TemplateView):

    template_name = "regulations/supplemental_content.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
