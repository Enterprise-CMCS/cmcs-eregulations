from datetime import date
from collections import OrderedDict
from unittest.mock import patch

import httpx
from rest_framework import status
from rest_framework.test import APITestCase

from regcore.models import Part
from regcore.search.models import Synonym


class RegcoreSerializerTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        depth = {'type': 'title', 'label': 'Title 42 - Public Health', 'parent': [], 'reserved': False, 'identifier': ['42'],
                 'label_level': 'Title 42', 'parent_type': '', 'descendant_range': None, 'label_description': 'Public Health'},\
                {'type': 'chapter', 'label':
                 ' Chapter IV - Centers for Medicare & Medicaid Services, Department of Health and Human Services',
                 'parent': ['42'], 'reserved': False,
                 'identifier': ['IV'], 'label_level': ' Chapter IV', 'parent_type': 'title', 'descendant_range': ['400', '699'],
                 'label_description':
                 'Centers for Medicare &amp; Medicaid Services, Department of Health and Human Services'},\
                {'type': 'subchapter', 'label': 'Subchapter C - Medical Assistance Programs', 'parent': ['IV'],
                 'reserved': False, 'identifier': ['C'], 'label_level': 'Subchapter C', 'parent_type': 'chapter',
                 'descendant_range': ['430', '456'], 'label_description': 'Medical Assistance Programs'},\
                 {'type': 'part', 'label': 'Part 432 - State Personnel Administration',
                  'parent': ['C'], 'reserved': False, 'identifier': ['432'], 'label_level': 'Part 432',
                  'parent_type': 'subchapter', 'descendant_range': ['432.1', '432.55'],
                  'label_description': 'State Personnel Administration'}
        structure = {"type": "title", "children": [{"type:": "part", "label": 400, "children": ["part content"]}]}
        Part.objects.all().delete()
        Part.objects.create(title='42', date="2020-06-30", last_updated="2022-09-21 08:36:45.735759", depth=2,
                            structure=structure, name=400, document={"document": "test"}, depth_stack=depth)
        s1, _ = Synonym.objects.get_or_create(isActive=True, baseWord="Syn1")
        s2, _ = Synonym.objects.get_or_create(isActive=True, baseWord="S2")
        s2.synonyms.set([s1])

    def test_get_title(self):
        payload = [
            42
        ]
        response = self.client.get("/v3/titles")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data, payload)

    def test_get_toc(self):
        toc = {'type': 'title', 'label': 'Title 42 - Public Health', 'parent': [],
               'reserved': False, 'identifier': ['42'], 'label_level': 'Title 42',
               'parent_type': '', 'descendant_range': None,
               'label_description': 'Public Health', 'children':
               [OrderedDict(
                    [('type', 'chapter'),
                     ('label', 'Chapter IV - Centers for Medicare & Medicaid Services, Department of Health and Human Services'),
                     ('parent', ['42']), ('reserved', False),
                     ('identifier', ['IV']),
                     ('label_level', 'Chapter IV'),
                     ('parent_type', 'title'),
                     ('descendant_range', ['400', '699']),
                     ('label_description',
                        'Centers for Medicare &amp; Medicaid Services, Department of Health and Human Services'),
                     ('children',
                        [OrderedDict([('type', 'subchapter'), ('label', 'Subchapter C - Medical Assistance Programs'),
                                      ('parent', ['IV']), ('reserved', False), ('identifier', ['C']),
                                      ('label_level', 'Subchapter C'),
                                      ('parent_type', 'chapter'),
                                      ('descendant_range', ['430', '456']),
                                      ('label_description', 'Medical Assistance Programs'),
                                      ('children',
                                       [OrderedDict([('type', 'part'),
                                                     ('label', 'Part 432 - State Personnel Administration'),
                                                     ('parent', ['C']),
                                                     ('reserved', False),
                                                     ('identifier', ['432']),
                                                     ('label_level', 'Part 432'),
                                                     ('parent_type', 'subchapter'),
                                                     ('descendant_range', ['432.1', '432.55']),
                                                     ('label_description', 'State Personnel Administration'),
                                                     ('children', [])])])])])])]}

        response = self.client.get("/v3/title/42/toc")

        self.assertEqual(response.data, toc)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_get_parts(self):
        parts = [{
            "id": 1,
            "name": "400",
            "date": "2020-06-30",
            "last_updated": '2022-09-26 15:15:27.313705',
            "depth": 2
        }]
        response = self.client.get("/v3/title/42/parts")
        x = response.data
        x = dict(x[0])
        self.assertEqual(x['name'], parts[0]['name'])
        self.assertEqual(x['depth'], parts[0]['depth'])
        self.assertEqual(x['id'], parts[0]['id'])

    def test_get_synonyms(self):
        response = self.client.get("/v3/synonym/S2")
        data = dict(response.data[0])
        synonyms = dict(data)
        self.assertEqual(synonyms['synonyms'], [{'baseWord': "Syn1", "isActive": True}])
        response = self.client.get("/v3/synonym/Syn1")
        data = dict(response.data[0])
        synonyms = dict(data)
        self.assertEqual(synonyms['synonyms'], [{'baseWord': "S2", "isActive": True}])

    def test_get_title_versions(self):
        response = self.client.get("/v3/title/42/versions")
        data = dict(response.data[0])
        self.assertEqual(data, {'date': '2020-06-30', 'part_name': ['400']})

    def test_get_part_versions(self):
        response = self.client.get("/v3/title/42/part/400/versions")
        data = response.data
        self.assertEqual(data, [date(2020, 6, 30)])

    @patch("regcore.v3views.history.get_year_data")
    def test_get_historical_sections(self, get_year_data):
        get_year_data.return_value = httpx.Response(status_code=400)
        data = self.client.get("/v3/title/42/part/433/history/section/50").data
        self.assertEqual(data, [])

        get_year_data.return_value = httpx.Response(
            status_code=302,
            headers={
                "location": "http://a.link.to.govinfo.gov/xyz.pdf",
            }
        )
        data = self.client.get("/v3/title/42/part/433/history/section/50").data
        self.assertEqual(len(data), date.today().year - 1996 + 1)
        self.assertEqual(data[0], OrderedDict([("year", "1996"), ("link", "http://a.link.to.govinfo.gov/xyz.pdf")]))

        get_year_data.return_value = httpx.Response(status_code=404)
        data = self.client.get("/v3/title/42/part/433/history/section/50").data
        self.assertEqual(len(data), date.today().year - 1996 + 1)
        self.assertEqual(data[0], OrderedDict([("year", "1996"), ("link", None)]))
