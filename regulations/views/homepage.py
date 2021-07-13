from datetime import date
import logging

from django.views.generic.base import TemplateView
from requests import HTTPError

from regcore.models import Part
from .utils import get_structure


logger = logging.getLogger(__name__)


class HomepageView(TemplateView):

    template_name = 'regulations/homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        c = {}

        today = date.today()
        parts = Part.objects.effective(today)
        if not parts:
            return context

        full_structure = get_structure(parts)

        c = {
            'structure': full_structure,
            'regulations': parts,
            'cfr_title_text': parts[0].structure['label_description'],
            'cfr_title_number': parts[0].structure['identifier'],
        }

        return {**context, **c}
