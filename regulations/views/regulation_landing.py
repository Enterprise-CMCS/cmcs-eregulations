from datetime import date, datetime
from requests import HTTPError
from django.views.generic.base import TemplateView
from django.http import Http404

from regulations.generator import api_reader

client = api_reader.ApiReader()


class RegulationLandingView(TemplateView):

    template_name = "regulations/regulation_landing.html"

    sectional_links = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = self.kwargs.get("title")
        reg_part = self.kwargs.get("part")

        try:
            current = client.toc(date.today(), title, reg_part)
        except HTTPError:
            raise Http404

        parts = client.effective_title_parts(date.today(), title)
        reg_version = current['date']
        toc = current['toc']
        part_label = toc['label_description']

        c = {
            'toc': toc,
            'title': title,
            'version': reg_version,
            'part': reg_part,
            'part_label': part_label,
            'reg_part': reg_part, 'parts': parts,
            'last_updated': datetime.fromisoformat(current['last_updated']),
            'content': [
                'regulations/partials/landing_%s.html' % reg_part,
                'regulations/partials/landing_default.html',
            ],
        }

        return {**context, **c}
