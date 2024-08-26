import json
from collections import OrderedDict
from datetime import date
from unittest.mock import patch

import httpx
from rest_framework import status
from rest_framework.test import APITestCase

from regcore.models import Part


class RegcoreSerializerTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        with open("regcore/tests/fixtures/depth.json") as f:
            depth = json.load(f)

        structure = {"type": "title", "children": [{"type:": "part", "label": 400, "children": ["part content"]}]}
        Part.objects.all().delete()
        Part.objects.create(title='42', date="2020-06-30", last_updated="2022-09-21 08:36:45.735759", depth=2,
                            structure=structure, name=400, document={"document": "test"}, depth_stack=depth)

    def test_get_title(self):
        payload = [
            42
        ]
        response = self.client.get("/v3/titles")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data, payload)

    def test_get_toc(self):
        response = self.client.get("/v3/title/42/toc")

        self.assertEqual(response.data['type'], "title")
        self.assertEqual(response.data['children'][0]['type'], "chapter")
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

    def test_get_title_versions(self):
        response = self.client.get("/v3/title/42/versions")
        data = dict(response.data[0])
        self.assertEqual(data, {'date': '2020-06-30', 'part_name': ['400']})

    def test_get_part_versions(self):
        response = self.client.get("/v3/title/42/part/400/versions")
        data = response.data
        self.assertEqual(data, [date(2020, 6, 30)])

    @patch("regcore.views.history.get_year_data")
    def test_get_historical_sections(self, get_year_data):
        # Test if year is not valid
        get_year_data.return_value = httpx.Response(status_code=400)
        data = self.client.get("/v3/title/42/part/433/history/section/50").data
        self.assertEqual(data, [])

        # Test if year is valid
        get_year_data.return_value = httpx.Response(
            status_code=302,
            headers={
                "location": "http://a.link.to.govinfo.gov/xyz.pdf",
            }
        )
        data = self.client.get("/v3/title/42/part/433/history/section/50").data
        self.assertEqual(len(data), date.today().year - 1996 + 1)
        self.assertEqual(data[0], OrderedDict([("year", "1996"), ("link", "http://a.link.to.govinfo.gov/xyz.pdf")]))

        # Test if we get a 404 for a specific year
        get_year_data.return_value = httpx.Response(status_code=404)
        data = self.client.get("/v3/title/42/part/433/history/section/50").data
        self.assertEqual(len(data), date.today().year - 1996 + 1)
        self.assertEqual(data[0], OrderedDict([("year", "1996"), ("link", None)]))

        # Test if connection times out, generally meaning year is not valid (same as 400 behavior)
        get_year_data.side_effect = httpx.TimeoutException(message="Connection timed out")
        data = self.client.get("/v3/title/42/part/433/history/section/50").data
        self.assertEqual(data, [])
