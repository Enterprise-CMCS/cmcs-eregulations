from requests import HTTPError
from django.views.generic.base import TemplateView
from django.http import Http404
from datetime import date

from regcore.models import Part


class RegulationLandingView(TemplateView):

    template_name = "regulations/regulation_landing.html"

    sectional_links = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = self.kwargs.get("title")
        reg_part = self.kwargs.get("part")

        try:
            current = Part.objects.effective(date.today()).get(title=title, name=reg_part)
        except HTTPError:
            raise Http404

        parts = Part.objects.effective(date.today()).filter(title=title)
        reg_version = current.date.isoformat()
        toc = current.toc
        part_label = toc['label_description']
        authority = current.document['authority']
        source = current.document['source']
        editorial_note = current.document['editorial_note']

        c = {
            'toc': toc,
            'title': title,
            'version': reg_version,
            'part': reg_part,
            'part_label': part_label,
            'reg_part': reg_part, 'parts': parts,
            'last_updated': current.last_updated,
            'authority': authority,
            'source': source,
            'editorial_note': editorial_note,
            'content': [
                'regulations/partials/landing_%s.html' % reg_part,
                'regulations/partials/landing_default.html',
            ],
        }

        return {**context, **c}
