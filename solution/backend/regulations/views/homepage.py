from datetime import date
import logging

from django.views.generic.base import TemplateView

from regcore.models import Part
from regcore.serializers.toc import FrontPageTOCSerializer


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

        queryset = Part.objects.order_by("title", "name", "-date").distinct("title", "name").values_list("depth_stack", flat=True)
        full_structure = FrontPageTOCSerializer(queryset, many=True).data

        c = {
            'structure': full_structure,
            'regulations': parts,
            'cfr_title_text': parts[0].structure['label_description'],
            'cfr_title_number': parts[0].structure['identifier'],
        }

        return {**context, **c}
