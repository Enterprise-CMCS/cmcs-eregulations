from datetime import date
from regcore.models import Part
from regcore.search.models import Synonym
from rest_framework import status
from collections import OrderedDict
from rest_framework.test import APITestCase
from unittest.mock import Mock, patch
async def mock_gov_info_400(section,year,client):
    mock_response = Mock()
    if year ==2020:
        mock_response.headers = {"location": "govinfo.gov"}
        mock_response.status_code = 302
    elif year == 2022:
        mock_response.status_code = 200
    else:
        mock_response.status_code = 400
    return mock_response
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
    @patch("regcore.v3views.history.get_history_data", mock_gov_info_400)
    def test_get_historical_sections(self):
        data = self.client.get("/v3/title/42/part/433/history/section/50").data

        self.assertEqual(data[0]['link'], "govinfo.gov")
        self.assertEqual(data[0]['year'], "2020")
        self.assertEqual(data[1]['year'], '2022')
        self.assertIsNone(data[1]['link'])
        # if not data:
        #     raise AssertionError("no years present for known-good section")
        # if "year" not in data[0] or "link" not in data[0]:
        #     raise AssertionError("missing one of 'year' or 'link' in response")
        # if data[0]["year"] != "1996":
        #     raise AssertionError("known-good section doesn't contain 1996")
