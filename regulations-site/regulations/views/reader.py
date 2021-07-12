from django.views.generic.base import (
    TemplateView,
    View,
)
from django.http import Http404
from django.urls import reverse
from django.http import HttpResponseRedirect

from regulations.generator import api_reader
from regulations.views.mixins import CitationContextMixin
from regulations.views.utils import find_subpart
from regulations.views.errors import NotInSubpart


class ReaderView(CitationContextMixin, TemplateView):

    template_name = 'regulations/reader.html'

    sectional_links = True

    client = api_reader.ApiReader()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        reg_version = context["version"]
        reg_part = context["part"]
        reg_title = context["title"]
        tree = self.client.part(reg_version, reg_title, reg_part)
        versions = self.get_versions(reg_title, reg_part)
        parts = self.client.effective_title_parts(reg_version, reg_title)
        document = tree['document']
        toc = tree['toc']
        part_label = toc['label_description']

        c = {
            'tree':         self.get_content(context, document, toc),
            'title':        reg_title,
            'reg_part':     reg_part,
            'part_label':   part_label,
            'toc':          toc,
            'parts':        parts,
            'versions':     versions,
        }

        return {**context, **c}

    def get_versions(self, title, part):
        versions = self.client.regversions(title, part)
        if versions is None:
            raise Http404
        return versions

    def get_content(self, context, document, toc):
        raise NotImplementedError()


class PartReaderView(ReaderView):

    def get_content(self, context, document, structure):
        return document


class SubpartReaderView(ReaderView):
    def get_content(self, context, document, toc):
        # using tree['structure'] find subpart requested then extract that data
        subpart = context['subpart']
        subpart_index = -1

        for i in range(len(toc['children'])):
            child = toc['children'][i]
            if 'type' in child and 'identifier' in child:
                if child['type'] == 'subpart' and child['identifier'][0] == subpart:
                    subpart_index = i

        if subpart_index == -1:
            raise Http404

        return document['children'][subpart_index]


class SectionReaderView(View):
    def get(self, request, *args, **kwargs):
        url_kwargs = {
            "title": kwargs.get("title"),
            "part": kwargs.get("part"),
            "version": kwargs.get("version"),
        }

        client = api_reader.ApiReader()

        if url_kwargs['version'] is None:
            versions = client.regversions(kwargs.get("title"), url_kwargs['part'])
            if versions is None:
                raise Http404
            url_kwargs['version'] = versions[0]['date']

        try:
            toc = client.toc(url_kwargs['version'], kwargs.get("title"), url_kwargs['part'])['toc']

            subpart = find_subpart(kwargs.get("section"), toc)
            if subpart is not None:
                url_kwargs["subpart"] = subpart
        except NotInSubpart:
            pass

        url = reverse("reader_view", kwargs=url_kwargs)
        return HttpResponseRedirect(url)
