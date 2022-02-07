from django.views.generic.base import (
    TemplateView,
    View,
)
from django.http import Http404
from django.urls import reverse
from django.http import HttpResponseRedirect

from regcore.models import Part
from supplemental_content.models import Category
from regulations.views.mixins import CitationContextMixin
from regulations.views.utils import find_subpart
from regulations.views.errors import NotInSubpart

from datetime import datetime


class ReaderView(CitationContextMixin, TemplateView):

    template_name = 'regulations/reader.html'

    sectional_links = True

    def get_context_data(self, **kwargs):
        start = datetime.now().timestamp()

        context = super().get_context_data(**kwargs)

        reg_version = context["version"]
        reg_part = context["part"]
        reg_title = context["title"]

        query = Part.objects.effective(reg_version).get(title=reg_title, name=reg_part)

        versions = self.get_versions(reg_title, reg_part)
        version_info = self.get_version_info(reg_version, reg_title, reg_part)

        parts = Part.objects.filter(title=reg_title).effective(reg_version)
        document = query.document
        toc = query.toc
        part_label = toc['label_description']
        tree = self.get_content(context, document, toc)
        node_list = self.get_supp_content_params(context, [tree])
        categories = list(Category.objects.all().order_by('order').values())

        c = {
            'tree':         tree,
            'title':        reg_title,
            'reg_part':     reg_part,
            'part_label':   part_label,
            'toc':          toc,
            'parts':        parts,
            'versions':     versions,
            'node_list':    node_list,
            'view_type':    self.get_view_type(),
            'categories':   categories,
        }

        end = datetime.now().timestamp()

        print(f'<<<<<<<<<< GET DATA START {start} - {end} END >>>>>>>>>>>>>>>')

        return {**context, **c, **version_info}

    def get_view_type(self):
        raise NotImplementedError()

    def get_versions(self, title, part):
        versions = Part.objects.versions(title, part)
        if versions is None:
            raise Http404
        return versions

    def get_content(self, context, document, toc):
        raise NotImplementedError()

    def get_supp_content_params(self, context, tree):
        return {
            "sections": self.get_sections(context, tree),
            "subparts": self.get_subparts(context, tree),
        }

    def get_nodes_by_type(self, tree, type, label_index):
        nodes = []
        for node in tree:
            if node.get("node_type") == type:
                nodes.append(node["label"][label_index])
            elif node.get("children") is not None and len(node["children"]) > 0:
                nodes = nodes + self.get_nodes_by_type(node["children"], type, label_index)
        return nodes

    def get_sections(self, context, tree):
        return self.get_nodes_by_type(tree, "SECTION", 1)

    def get_subparts(self, context, tree):
        return self.get_nodes_by_type(tree, "SUBPART", 0)

    def get_version_info(self, version, title, part):
        versions = self.get_versions(title, part)

        latestVersion = versions[0]['date']
        latestVersionString = datetime.strftime(latestVersion, "%Y-%m-%d")

        return {
            'version': version,
            'formattedLatestVersion': datetime.strftime(latestVersion, "%b %-d, %Y"),
            'isLatestVersion': version == latestVersionString
        }


class PartReaderView(ReaderView):

    def get_view_type(self):
        return "part"

    def get_content(self, context, document, structure):
        return document


class SubpartReaderView(ReaderView):

    def get_view_type(self):
        return "subpart"

    def get_subparts(self, context, tree):
        return [context["subpart"]]

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

        content = document['children'][subpart_index]
        return content


class SectionReaderView(View):
    def get(self, request, *args, **kwargs):
        url_kwargs = {
            "title": kwargs.get("title"),
            "part": kwargs.get("part"),
            "version": kwargs.get("version"),
        }

        if url_kwargs['version'] is None:
            versions = Part.objects.versions(kwargs.get("title"), url_kwargs['part'])
            if versions is None:
                raise Http404
            url_kwargs['version'] = versions[0]['date']

        try:
            toc = Part.objects.effective(url_kwargs['version']).get(title=kwargs.get("title"), name=url_kwargs['part']).toc

            subpart = find_subpart(kwargs.get("section"), toc)
            if subpart is not None:
                url_kwargs["subpart"] = subpart
        except NotInSubpart:
            pass

        url = reverse("reader_view", kwargs=url_kwargs)
        return HttpResponseRedirect(url)
