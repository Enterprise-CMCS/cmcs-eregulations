from django.contrib.sitemaps import Sitemap
from datetime import datetime
from django.urls import reverse

from regcore.models import Part
from resources.models import Resource


class PartSitemap(Sitemap):

    changefreq = "daily"
    priority = 0.5

    def processChildren(self, children, title, part, last_updated):
        results = []
        for child in children:
            if child.get('type', '') == 'subpart':
                results.append({
                    'title': title,
                    'part': part,
                    'subpart': child['identifier'][0],
                    'last_updated': last_updated
                })
            # This just ends up forwarding to the subchapter page so removing for now, but we can add back if needed
            # if child.get('type', '') == 'section':
            #    results.append({'title': title, 'part': part, 'section': child['identifier'][1]})
            if child['children']:
                childResults = self.processChildren(child['children'], title, part, last_updated)
                if childResults:
                    results = results + childResults
        return results

    def items(self):
        date = datetime.now()
        title = 42
        query = Part.objects.filter(title=title).filter(date__lte=date).order_by("name", "-date").distinct("name")
        results = []
        for p in query:
            results.append({
                'title': p.title,
                'part': p.name,
                'last_updated': p.last_updated
            })
            children = p.structure['children']
            results = results + self.processChildren(children, p.title, p.name, p.last_updated)

        return results

    def lastmod(self, obj):
        return obj['last_updated']

    def location(self, item):
        kwargs = {}
        for key in ['title', 'part', 'subpart']:
            if item.get(key):
                kwargs[key] = item[key]
        return reverse("reader_view", kwargs=kwargs)


class SupplementalContentSitemap(Sitemap):

    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Resource.objects.filter(approved=True)

    def lastmod(self, item):
        return item.updated_at

    def location(self, item):
        return reverse("supplemental_content", kwargs={"id": item.id})
