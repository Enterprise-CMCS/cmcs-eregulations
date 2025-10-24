from datetime import date, datetime

from django.http import Http404
from django.views.generic.base import TemplateView
from requests import HTTPError

from regcore.models import ECFRParserResult, Part


class RegulationLandingView(TemplateView):

    template_name = "regulations/regulation_landing.html"

    sectional_links = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = self.kwargs.get("title")
        reg_title_parser_success_date = ECFRParserResult.objects.filter(errors=0, title=title).order_by("-end").first()
        reg_part = self.kwargs.get("part")

        try:
            current = Part.objects.effective(date.today()).get(title=title, name=reg_part)
        except HTTPError:
            raise Http404

        parts = Part.objects.effective(date.today()).filter(title=title)
        reg_version = current.date.isoformat()
        reg_version_string = datetime.strftime(current.date, "%b %-d, %Y")
        toc = current.toc
        subchapter = current.subchapter
        part_label = toc['label_description']
        authority = current.document['authority']
        source = current.document['source']
        editorial_note = current.document['editorial_note']

        c = {
            'toc': toc,
            'title': title,
            'title_parser_success_date': reg_title_parser_success_date.end if reg_title_parser_success_date else None,
            'version': reg_version,
            'version_string': reg_version_string,
            'subchapter': subchapter,
            # last updated dates of Jan 1, 2017 are not meaningful
            'has_meaningful_latest_version_date': current.date > date(2017, 1, 1),
            'part': reg_part,
            'part_label': part_label,
            'reg_part': reg_part, 'parts': parts,
            'authority': authority,
            'source': source,
            'editorial_note': editorial_note,
            'content': [
                'regulations/partials/landing_%s.html' % reg_part,
                'regulations/partials/landing_default.html',
            ],
        }

        return {**context, **c}
