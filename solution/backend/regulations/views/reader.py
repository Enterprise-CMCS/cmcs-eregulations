from datetime import date, datetime

from django.db.models import Count, Q
from django.http import (
    Http404,
    HttpResponseRedirect,
)
from django.urls import reverse
from django.views.generic.base import (
    TemplateView,
    View,
)

from regcore.models import Part
from regulations.models import (
    RegulationLinkConfiguration,
    StatuteLinkConfiguration,
    StatuteLinkConverter,
)
from regulations.views.errors import NotInSubpart
from regulations.views.mixins import CitationContextMixin
from regulations.views.utils import find_subpart
from resources.models import (
    AbstractCitation,
    PublicCategory,
)


class ReaderView(CitationContextMixin, TemplateView):

    template_name = 'regulations/reader.html'

    sectional_links = True

    def get_context_data(self, **kwargs):
        start = datetime.now().timestamp()

        context = super().get_context_data(**kwargs)

        reg_version = context.get("version", datetime.strftime(datetime.now(), "%Y-%m-%d"))
        reg_part = context["part"]
        reg_title = context["title"]

        query = Part.objects.effective(reg_version).get(title=reg_title, name=reg_part)

        versions = self.get_versions(reg_title, reg_part)
        version_info = self.get_version_info(reg_version, reg_title, reg_part)

        parts = Part.objects.filter(title=reg_title).effective(reg_version)
        document = query.document
        toc = query.toc
        subchapter = query.subchapter
        part_label = toc['label_description']
        tree = self.get_content(context, document, toc)
        node_list = self.get_supp_content_params(context, [tree])
        categories = list(PublicCategory.objects.order_by('order').values())

        locations = AbstractCitation.objects.filter(part=reg_part).select_subclasses().annotate(
            num_locations=Count(
                'resources', filter=Q(resources__approved="t")
            )).filter(
            num_locations__gt=0)
        resource_count = {}
        for location in locations:
            resource_count[location.display_name] = location.num_locations

        conversions = {}
        for section, usc, act, title in StatuteLinkConverter.objects.values_list("section", "usc", "act", "title"):
            if act not in conversions:
                conversions[act] = {}
            conversions[act][section] = {
                "title": title,
                "usc": usc,
            }

        statute_link_config = StatuteLinkConfiguration.get_solo()
        reg_link_config = RegulationLinkConfiguration.get_solo()

        link_config = {
            "link_statute_refs": statute_link_config.link_statute_refs,
            "link_usc_refs": statute_link_config.link_usc_refs,
            "statute_ref_exceptions": statute_link_config.statute_ref_exceptions_dict,
            "usc_ref_exceptions": statute_link_config.usc_ref_exceptions_dict,
            "link_cfr_refs": reg_link_config.link_cfr_refs,
            "cfr_ref_exceptions": reg_link_config.cfr_ref_exceptions_dict,
        }

        user = self.request.user
        is_user_authenticated = user.is_authenticated

        c = {
            'tree':         tree,
            'title':        reg_title,
            'reg_part':     reg_part,
            'part_label':   part_label,
            'toc':          toc,
            'subchapter':   subchapter,
            'parts':        parts,
            'versions':     versions,
            'node_list':    node_list,
            'view_type':    self.get_view_type(),
            'categories':   categories,
            'resource_count': resource_count,
            'link_conversions': conversions,
            'link_config': link_config,
            'is_user_authenticated': is_user_authenticated,
            'user': user,
        }

        end = datetime.now().timestamp()

        print(f'<<<<<<<<<< GET DATA START {start} - {end} END >>>>>>>>>>>>>>>')

        return {**context, **c, **version_info}

    def get(self, request, *args, **kwargs):
        if kwargs.get('version') is None:
            versions = Part.objects.versions(kwargs.get("title"), kwargs.get('part'))
            if versions is None:
                raise Http404
            kwargs['version'] = versions[0]['date']
            return HttpResponseRedirect(reverse('reader_view', kwargs=kwargs))
        return super().get(request, *args, **kwargs)

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

        latest_version = versions[0]['date']
        latest_version_string = datetime.strftime(latest_version, "%Y-%m-%d")

        return {
            'version': version,
            'formatted_latest_version': datetime.strftime(latest_version, "%b %-d, %Y"),
            'is_latest_version': version == latest_version_string,
            # last updated dates of Jan 1, 2017 are not meaningful
            'has_meaningful_latest_version_date': latest_version > date(2017, 1, 1)
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

        query_string = request.GET.get("q", None)

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

        redirect_url = url + "?highlight=" + query_string.replace('%', '%25') if query_string else url

        return HttpResponseRedirect(redirect_url)


class AppendixReaderView(ReaderView):
    def get_view_type(self):
        return "appendix"

    def get_content(self, context, document, toc):
        # Get the appendix identifier from the URL
        appendix_path = context.get('appendix')

        # Find the appendix in the document structure
        appendix_index = -1

        for i, child in enumerate(toc['children']):
            if ('type' in child and child['type'] == 'appendix' and
                'identifier' in child):
                # Compare the full identifier to find the exact appendix
                # Need to make a case-insensitive and format-insensitive comparison

                # First, standardize both identifiers for comparison
                url_identifier = [part.upper() for part in appendix_path]
                child_identifier = [part.upper() for part in child['identifier']]

                # Check if the important parts match (Appendix number, part number)
                # For example, match ["APPENDIX", "VIII", "TO", "PART", "75"]
                # with ["APPENDIX", "VIII", "TO", "PART", "75"]

                # Find the appendix number index (usually index 1 if present)
                appendix_num_index = (1 if len(url_identifier) > 1 and
                                      url_identifier[1] not in ["TO", "PART"] else None)

                if appendix_num_index:
                    # Compare appendix number and part number
                    url_appendix_num = url_identifier[appendix_num_index]
                    child_appendix_num = (child_identifier[appendix_num_index]
                                          if len(child_identifier) > appendix_num_index else None)

                    # Get part numbers
                    url_part_index = (url_identifier.index("PART") + 1
                                      if "PART" in url_identifier else None)
                    child_part_index = (child_identifier.index("PART") + 1
                                        if "PART" in child_identifier else None)

                    url_part_num = (url_identifier[url_part_index]
                                    if url_part_index and url_part_index < len(url_identifier) else None)
                    child_part_num = (child_identifier[child_part_index]
                                      if child_part_index and child_part_index < len(child_identifier) else None)

                    # Match both appendix number and part number
                    if (url_appendix_num == child_appendix_num and
                            url_part_num == child_part_num):
                        appendix_index = i
                        context['appendix_data'] = child
                        break
                else:
                    # Handle case with no appendix number (just "Appendix to Part X")
                    # Compare just the part numbers
                    url_part_index = (url_identifier.index("PART") + 1
                                      if "PART" in url_identifier else None)
                    child_part_index = (child_identifier.index("PART") + 1
                                        if "PART" in child_identifier else None)

                    url_part_num = (url_identifier[url_part_index]
                                    if url_part_index and url_part_index < len(url_identifier) else None)
                    child_part_num = (child_identifier[child_part_index]
                                      if child_part_index and child_part_index < len(child_identifier) else None)

                    # If neither has an appendix number and part numbers match
                    if (("TO" in url_identifier and "TO" in child_identifier) and
                            url_part_num == child_part_num and
                            url_identifier[0] == child_identifier[0]):  # Both start with "APPENDIX"
                        appendix_index = i
                        context['appendix_data'] = child
                        break

        if appendix_index == -1:
            raise Http404

        content = document['children'][appendix_index]
        context['appendix'] = True  # Flag that we're viewing an appendix
        return content
