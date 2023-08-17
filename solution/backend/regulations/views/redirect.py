from django.http import Http404
from django.urls import reverse
from django.views.generic.base import RedirectView

from regcore.models import Part

ECFR_URL_FORMAT = "https://www.ecfr.gov/current/"


def find_node(node_children, node_type, id_index, id):
    for i in node_children:
        if i["node_type"].lower() == node_type.lower():
            if "-".join(i["label"][id_index:]) == id.lower():
                return i
            continue
        if "children" in i and i["children"]:
            s = find_node(i["children"], node_type, id_index, id)
            if s:
                return s
    return None


class RegulationRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        title = self.request.GET.get("title", None)
        part = self.request.GET.get("part", None)
        section = self.request.GET.get("section", None)
        paragraph = self.request.GET.get("paragraph", None)

        queryset = Part.objects.filter(title=title, name=part).order_by("name", "-date").distinct("name")

        if not queryset:
            # Title/part combo doesn't exist in eRegs, build eCFR URL and redirect
            url = f"{ECFR_URL_FORMAT}"
            if not title:
                raise Http404
            url += f"title-{title}/"
            if not part:
                return url
            url += f"part-{part}/"
            if not section:
                return url
            url += f"section-{part}.{section}"
            if not paragraph:
                return url
            url += f"#p-{part}.{section}" + "".join([f"({i})" for i in paragraph.split("-")])
            return url

        # Title/part combo exists in eRegs, build reverse params and redirect

        document = queryset[0].document
        date = queryset[0].date

        params = {
            "title": title,
            "part": part,
        }

        if not section:
            # No section defined, redirect to part TOC
            return reverse("reader_view", kwargs=params)

        # Attempt to find section
        node = find_node(document["children"], "section", 1, section)
        if not node:
            # No section, link to part level
            params["version"] = date
            return reverse("reader_view", kwargs=params)
        params["section"] = section

        # Attempt to find paragraph
        if paragraph and "children" in node and node["children"]:
            node = find_node(node["children"], "paragraph", 2, paragraph)
            if node:
                # Paragraph found, redirect to it
                return reverse("reader_view", kwargs=params) + f"#{part}-{section}-" + paragraph

        # Paragraph not defined or not found, redirect to section level
        return reverse("reader_view", kwargs=params) + f"#{part}-{section}"
