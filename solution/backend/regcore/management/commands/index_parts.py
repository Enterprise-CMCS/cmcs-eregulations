import json
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from regcore.models import Part


class Command(BaseCommand):
    help = 'Index Regcore.Part objects to open search'
    data = []
    openSearchURL = settings.OPENSEARCH_DSL['default']['hosts']
    count = 0
    url = f'http://{openSearchURL}:9200/_bulk'

    def process_node(self, node, name, title):

        if node.get('children'):
            for child in node['children']:
                if child.get('children'):
                    self.process_node(child, name, title)
                self.process_child(child, name, title)
        self.process_child(node, name, title)

    def process_child(self, child, name, title):
        if child.get('label'):
            if child.get('title'):
                child['text'] = child['title']
                del child['title']
            if child.get('children'):
                del child['children']
            if len(child["label"]) == 1 and child['node_type'] != "PART":
                child["label"].insert(0, name)
            index = f'{{"index": {{"_index": "parts", "_id": "{title}.{".".join(child["label"])}"}}}}'
            self.data.append(index)
            self.data.append(json.dumps(child))

    def handle(self, *args, **options):
        # get all of the parts in date order, oldest to newest
        parts = Part.objects.all().order_by('date')
        for part in parts:
            print(type(part.document))
            self.process_node(part.document, part.name, part.title)
        print(len(self.data))
        count = 0
        chunk = 1000
        while count < len(self.data):
            payload = '\n'.join(self.data[count:count + chunk])
            payload = payload + '\n'

            r = requests.post(
                self.url,
                data=payload,
                headers={"Content-Type": "application/x-ndjson"}
            )
            count += chunk
            print(r.status_code)
            print(count)
