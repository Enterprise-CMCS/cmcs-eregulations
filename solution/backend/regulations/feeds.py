from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from regcore.models import Part
from resources.models import AbstractResource
from django.contrib.syndication.views import Feed


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

    def __init__(self):
        self.path = None

    def get_feed(self, obj, request):
        self.path = request.path

        feedgen = super().get_feed(obj, request)
        feedgen.content_type = 'application/xml'  # New standard
        return feedgen

    def items(self):
        results = []
        resources = AbstractResource.objects.filter(approved=True).select_subclasses()
        for resource in resources:
            results.append({
                'date': resource.updated_at,
                'description': resource.description.replace('\x02', ''),
                'url': resource.url,
            })
        return results

    def item_title(self, item):
        return item['date'].strftime("%b %d, %Y")

    def item_pubdate(self, item):
        return item['date']

    def item_description(self, item):
        return item['description']

    def item_link(self, item):
        url = item['url']
        if url:
            return url
        else:
            return 'https://www.google.com'


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
