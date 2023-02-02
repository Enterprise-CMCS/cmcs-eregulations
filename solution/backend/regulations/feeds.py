from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from regcore.models import Part
from resources.models import AbstractResource
from django.contrib.syndication.views import Feed
from datetime import datetime
from dateutil import parser
import re

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
    link = '/latest/feed/'
    description = 'Displays the latest federal register documents'

    def get_feed(self, obj, request):
        feedgen = super().get_feed(obj, request)
        feedgen.content_type = 'application/xml'  # New standard
        return feedgen

    def get_date(self, date_time):
        date = parser.parse(date_time) if date_time else ''
        return date

    def items(self):
        results = []
        resources = AbstractResource.objects.filter(approved=True).select_subclasses()
        # if there is no date value then we will use this placeholder date for the datepublished.
        place_holder_pubdate = '1970-01-01'
        for resource in resources:
            results.append({
                'date': self.get_date(resource.date),
                'date_published': resource.date if resource.date else place_holder_pubdate,
                'description': resource.description.replace('\x02', ''),
                'url': resource.url,
                'name': resource.name,
            })
        return results

    def item_title(self, item):
        date = item['date'].strftime("%b %d, %Y") if item['date'] else ''
        if date and item['name']:
            return f"{date} | {item['name']}"
        else:
            return date if date else item['name']

    def item_pubdate(self, item):
        return self.get_date(item['date_published'])

    def item_description(self, item):
        return item['description']

    def item_link(self, item):
        return item['url'] if item['url'] else '/'


class PartSitemap(Sitemap, FeedData):
    changefreq = 'daily'
    priority = 0.5

    def items(self):
        date = datetime.now()
        title = 42
        query = Part.objects.filter(title=title).filter(date__lte=date).order_by('name', '-date').distinct('name')
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
        return reverse('reader_view', kwargs=kwargs)


class SupplementalContentSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.5

    def items(self):
        return AbstractResource.objects.filter(approved=True)

    def lastmod(self, item):
        return item.updated_at

    def location(self, item):
        return reverse('supplemental_content', kwargs={'id': item.id})
