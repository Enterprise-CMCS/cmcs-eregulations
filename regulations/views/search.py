from datetime import date

from django.views.generic.base import TemplateView

from regcore.models import Part
from regcore.search.models import SearchIndex
from .utils import get_structure


class SearchView(TemplateView):

    template_name = 'regulations/search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        results = get_data(self.request.GET.get("q"))
        today = date.today()
        parts = Part.objects.effective(today)
        structure = get_structure(parts)
        c = {
            'parts': parts,
            'toc': structure,
            'results': results,
        }
        return {**context, **c, **self.request.GET.dict()}


def get_data(query):
    return SearchIndex.objects.search(query)
