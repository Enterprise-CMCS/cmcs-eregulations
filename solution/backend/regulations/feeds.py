from django.contrib.sitemaps import Sitemap
from datetime import datetime
from django.urls import reverse
from django.views.generic.base import TemplateView

from regcore.models import Part
from resources.models import AbstractResource
from django.contrib.syndication.views import Feed
import os


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
    link = "latest/feed"
    description = 'Displays the latest federal register documents'

    def get_feed(self, obj, request):
        self.is_secure = request.is_secure()
        self.host = request.get_host()
        feedgen = super().get_feed(obj, request)
        feedgen.content_type = 'application/xml'  # New standard
        return feedgen

    def items(self):
        date = datetime.now()
        title = 42
        query = Part.objects.filter(title=title).filter(date__lte=date).order_by('name', '-date').distinct('name')
        results = []
        for p in query:
            results.append({
                'title': p.title,
                'part': p.name,
                'last_updated': p.last_updated,
                'document_title': p.document['title'],
                'document_label': 'Part {}'.format(p.document['label'][0]),
            })
            children = p.structure['children']
            results = results + self.processChildren(children, p.title, p.name, p.last_updated)

        return results

    def item_title(self, item):
        if 'document_label' in item:
            return item['document_label']
        else:
            return '{} {} Subpart {}'.format(item['title'], item['part'], item['subpart'])

    def item_pubdate(self, item):
        return item['last_updated']

    def item_description(self, item):
        if 'document_title' in item:
            return item['document_title']
        else:
            return '{} {} Subpart {}'.format(item['title'], item['part'], item['subpart'])

    def item_link(self, item):
        protocol = "https" if self.is_secure else "http"
        db_name = "" if os.environ.get("DB_NAME") is None else os.environ.get("DB_Name")
        if db_name == 'eregs':
            return "{}/{}".format(item['title'], item['part'])

        else:
            return f"{protocol}://{self.host}/{item['title']}/{item['part']}"

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
