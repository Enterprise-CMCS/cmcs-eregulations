from django.contrib.syndication.views import Feed
from django.urls import reverse
from datetime import datetime
from regcore.models import Part
from resources.models import AbstractResource


class PartFeed(Feed):
    def get_feed(self, obj, request):
        feedgen = super().get_feed(obj, request)
        feedgen.content_type = 'application/xml'  # New standard
        return feedgen
    title = 'Federal Register documents RSS Feed'
    link = '/latest/feed'
    description = 'Displays the latest federal register documents'

    def processChildren(self, children, title, part, last_updated):
        results = []
        for child in children:
            if child.get('type', '') == 'subpart':
                results.append({
                    'title': title,
                    'part': part,
                    'subpart': child['identifier'][0],
                    'last_updated': last_updated,
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

    def item_description(self, item):
        if 'document_title' in item:
            return item['document_title']
        else:
            return '{} {} Subpart {}'.format(item['title'], item['part'], item['subpart'])

    def item_link(self, item):
        return '/{}/{}'.format(item['title'], item['part'])


class SupplementalContentFeed(Feed):
    title = 'supplemental content feed'
    link = '/supplemental_content/'
    description = 'Updates on changes and additions to supplemental content.'

    def items(self):
        return AbstractResource.objects.filter(approved=True)

    # def item_title(self, item):
        # return item.title

    # def item_description(self, item):
        # return item.description

    def item_link(self, item):
        return reverse('supplemental_content', kwargs={'id': item.id})
