from django.urls import reverse
from resources.models import AbstractResource
from django.contrib.syndication.views import Feed
from dateutil import parser


class ResourceFeed(Feed):
    title = 'Resources RSS Feed'
    link = '/latest/feed/'
    description = 'Displays the latest Resources RSS feed'

    def __init__(self):
        self.feed_number = None

    def get_object(self, request, feed_number):
        page_size = 900
        start = (feed_number - 1) * page_size
        end = feed_number * page_size
        self.feed_number = feed_number
        return {'start': start, 'end': end}

    def get_feed(self, obj, request):
        feedgen = super().get_feed(obj, request)
        feedgen.content_type = 'application/xml'  # New standard
        return feedgen

    def get_date(self, date_time):
        date = parser.parse(date_time) if date_time else ''
        return date

    def items(self, obj):
        start = obj['start']
        end = obj['end']
        results = []
        resources = AbstractResource.objects.filter(approved=True).select_subclasses()[start:end]
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
        return item['name'] if item['name'] else "-"

    def item_pubdate(self, item):
        return self.get_date(item['date_published'])

    def item_description(self, item):
        return item['description']

    def item_link(self, item):
        return item['url'] if item['url'] else '/'

    def link(self):
        # Add the current feed number to the link URL to distinguish between multiple feeds
        return reverse('latest_feed', args=[self.feed_number])
