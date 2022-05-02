from datetime import date

from django.views.generic.base import TemplateView
from django.http import Http404

from regcore.models import Part
from regcore.search.models import SearchIndex, Synonym
from .utils import get_structure


class SearchView(TemplateView):

    template_name = 'regulations/search.html'

    def get_context_data(self, **kwargs):
        query = self.request.GET.get("q")
        context = super().get_context_data(**kwargs)
        today = date.today()
        results = SearchIndex.objects.effective(today).search(query)
        parts = Part.objects.effective(today)
        if not parts:
            raise Http404
        structure = get_structure(parts)
        synonym = Synonym.objects.filter(isActive=True, baseWord__iexact=query.strip('\"')).first()
        c = {
            'parts': parts,
            'toc': structure,
            'results': results,
            'synonym': synonym,
            'unquoted_search': not query.startswith('"') and not query.endswith('"') and len(query.split(" ")) > 1,
            'query': query,
        }
        return {**context, **c, **self.request.GET.dict()}
