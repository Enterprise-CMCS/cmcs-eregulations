from datetime import date

from django.views.generic.base import TemplateView

from regulations.generator.api_reader import ApiReader
from .utils import get_structure

client = ApiReader()


class SearchView(TemplateView):

    template_name = 'regulations/search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        results = get_data(self.request.GET.get("q"))
        today = date.today()
        parts = client.effective_parts(today)
        structure = get_structure(parts)
        c = {
            'parts': parts,
            'toc': structure,
            'results': results,
        }
        return {**context, **c, **self.request.GET.dict()}


def get_data(query):
    return client.search(query)
