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

    def process_children(self, children):

        for child in children:
            if child.get('children'):
                self.process_children(child['children'])
            else:
                # print(child)
                if child.get('label'):
                    index = f'{{"index": {{"_index": "parts", "_id": "{".".join(child["label"])}"}}}}'
                    self.data.append(index)
                    self.data.append(json.dumps(child))


    def handle(self, *args, **options):
        # get all of the parts in date order, oldest to newest
        parts = Part.objects.all().order_by('date')
        for part in parts:
            self.process_children(part.document['children'])
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
