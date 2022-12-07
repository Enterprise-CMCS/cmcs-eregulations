from datetime import date

from django.views.generic.base import TemplateView
from django.http import Http404

from regcore.models import Part
from regcore.search.models import SearchIndex, Synonym
from .utils import get_structure, get_tag_contents


class SearchView(TemplateView):

    template_name = 'regulations/search_new.html'

    def get_context_data(self, **kwargs):
        query = self.request.GET.get("q")
        context = super().get_context_data(**kwargs)
        today = date.today()
        results = SearchIndex.objects.effective(today).search(query)
        results_list = []
        parts = Part.objects.effective(today)
        if not parts:
            raise Http404
        structure = get_structure(parts)
        synonym = None
        synonym_list = []
        if query:
            synonym = Synonym.objects.filter(isActive=True, baseWord__iexact=query.strip('\"')).first()
            if synonym:
                for syn in synonym.filtered_synonyms:
                    synonym_list.append(str(syn))

        c = {
            'parts': parts,
            'toc': structure,
            'results': results,
            'synonym': synonym,
            'synonym_list': synonym_list,
            'unquoted_search': query and not query.startswith('"') and not query.endswith('"') and len(query.split(" ")) > 1,
            'query': query,
        }

        return {**context, **c, **self.request.GET.dict()}
