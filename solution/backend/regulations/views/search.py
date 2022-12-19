from django.views.generic.base import TemplateView
from django.http import Http404

from regcore.models import Part
from regcore.search.models import SearchIndex, Synonym, SearchConfiguration
from .utils import get_structure, get_tag_contents


class SearchView(TemplateView):
    template_name = 'regulations/search.html'

    def get_configs(self, config):
        config = SearchConfiguration.objects.get(config=config)
        return config

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        host = self.request.get_host()

        c = {
            'host': host
         }

        return {**context, **c, **self.request.GET.dict()}
