from django.contrib.sitemaps import Sitemap
from datetime import datetime
from django.urls import reverse
from regcore.models import Part
from resources.models import AbstractResource
from django.contrib.syndication.views import Feed
from django.http.request import HttpRequest
from regcore.v3views.metadata import PartSectionsViewSet
import json

class FeedData:
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
            if child['children']:
                childResults = self.processChildren(child['children'], title, part, last_updated)
                if childResults:
                    results = results + childResults
        return results


class PartFeed(Feed, FeedData):
    title = 'Federal Register documents RSS Feed'
    link = "/latest/feed/"
    description = 'Displays the latest federal register documents'

    def __init__(self):
        self.path = None

    def get_feed(self, obj, request):
        self.path = request.path

        feedgen = super().get_feed(obj, request)
        feedgen.content_type = 'application/xml'  # New standard
        return feedgen

    def items(self):
        date = datetime.now()
        title = 42
        request = HttpRequest()
        request.method = "GET"
        view = PartSectionsViewSet.as_view({"get": "retrieve"})
        # Replace 42 and 433 below with your title and part variables from the Part model query above
        parts = Part.objects.all().order_by("name", "date").distinct("name")
        for part in parts:
            data = view(request=request, title=part.title, part=part.name, version="latest").data
            data = json.loads(json.dumps(data))
            results = []
            for p in data:
                results.append({
                    'title': part.title,
                    'date': part.date,
                    'part': p['identifier'][0],
                    'section': p['identifier'][1],
                    'last_updated': date,
                    'description': p['label_description'],
                    'parent_name': p['parent'][0],
                    'parent_type': p['parent_type'],
                })

        return results

    def get_title(self, item):
        return f"{item['title']} {item['part']} Section {item['section']}"

    def item_title(self, item):
        if 'document_label' in item:
            return item['document_label']
        else:
            return f"{item['title']} CFR {item['part']}.{item['section']}"

    def item_pubdate(self, item):
        return item['last_updated']

    def item_description(self, item):
        if 'description' in item:
            return item['description']
        else:
            return f"{item['title']} {item['part']} Section {item['section']}"

    def item_link(self, item):
        if item['parent_type'] == 'subpart':
            return f"{self.path}{item['title']}/{item['part']}/Subpart-{item['parent_name']}/#{item['part']}-{item['section']}".replace('/latest/feed', '')
        else:
            return f"{self.path}{item['title']}/{item['part']}/"


class SupplementalContentFeed(Feed):
    title = 'supplemental content feed'
    link = '/supplemental_content/'
    description = 'Updates on changes and additions to supplemental content.'

    def items(self):
        return AbstractResource.objects.filter(approved=True)

    def item_link(self, item):
        return reverse('supplemental_content', kwargs={'id': item.id})


class PartSitemap(Sitemap, FeedData):

    changefreq = "daily"
    priority = 0.5

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
        return AbstractResource.objects.filter(approved=True)

    def lastmod(self, item):
        return item.updated_at

    def location(self, item):
        return reverse("supplemental_content", kwargs={"id": item.id})
