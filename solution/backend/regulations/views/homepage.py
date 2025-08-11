import logging
from datetime import date

from django.db.models import Prefetch
from django.views.generic.base import TemplateView

from regcore.models import Part
from regcore.serializers.toc import FrontPageTOCSerializer
from regulations.middleware import get_hostname
from resources.models import AbstractCategory, ResourcesConfiguration

logger = logging.getLogger(__name__)


class HomepageView(TemplateView):

    template_name = 'regulations/homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        raise Exception(get_hostname())

        c = {}

        today = date.today()
        parts = Part.objects.effective(today)
        resources_config = ResourcesConfiguration.objects.prefetch_related(
            Prefetch("fr_link_category", AbstractCategory.objects.select_subclasses())).first()
        fr_docs_category_name = resources_config.fr_link_category.name if resources_config.fr_link_category else ""

        if not parts:
            return context

        queryset = Part.objects.order_by("title", "name", "-date").distinct("title", "name").values_list("depth_stack", flat=True)
        full_structure = FrontPageTOCSerializer(queryset, many=True).data

        c = {
            'structure': full_structure,
            'regulations': parts,
            'cfr_title_text': parts[0].structure['label_description'],
            'cfr_title_number': parts[0].structure['identifier'],
            'fr_docs_category_name': fr_docs_category_name,
        }

        return {**context, **c}
