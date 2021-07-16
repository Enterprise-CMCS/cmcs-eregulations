from datetime import date

from django.views.generic.base import TemplateView
from django.http import Http404

from regcore.models import Part
from regcore.search.models import SearchIndex
from .utils import get_structure


class SearchView(TemplateView):

    template_name = 'regulations/search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        results = SearchIndex.objects.effective(today).search(self.request.GET.get("q"))
        parts = Part.objects.effective(today)
        if not parts:
            raise Http404
        structure = get_structure(parts)
        c = {
            'parts': parts,
            'toc': structure,
            'results': results,
        }
        return {**context, **c, **self.request.GET.dict()}
