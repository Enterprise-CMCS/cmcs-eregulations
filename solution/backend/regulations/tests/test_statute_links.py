import json
from unittest import mock

from django.core.exceptions import ValidationError
from django.template import Context, Template
from django.test import SimpleTestCase, TestCase

from rest_framework import status
from rest_framework.test import APITestCase

from requests.exceptions import HTTPError

from regulations.admin import StatuteLinkConverterAdmin
from regulations.models import StatuteLinkConverter


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, status_code, text):
            self.status_code = status_code
            self.text = text

        def raise_for_status(self):
            if self.status_code != 200:
                raise HTTPError(f"status code is {self.status_code}: {self.text}")

    if args[0] == "http://test.com/test.xml":
        try:
            data = ""
            with open("regulations/tests/fixtures/statute_link_data.xml", "r") as f:
                for line in f:
                    data += line
            return MockResponse(200, data)
        except Exception as e:
            return MockResponse(400, str(e))
    elif args[0] == "http://test.com/test_aca.xml":
        try:
            data = ""
            with open("regulations/tests/fixtures/statute_link_data_aca.xml", "r") as f:
                for line in f:
                    data += line
            return MockResponse(200, data)
        except Exception as e:
            return MockResponse(400, str(e))
    elif args[0] == "http://test.com/invalid.xml":
        return MockResponse(200, "Hello World")
    return MockResponse(404, "invalid URL")


class TestStatuteLinkImport(TestCase):
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_try_import_single_title(self, mocked_get):
        with open("regulations/tests/fixtures/statute_link_golden.json", "r") as f:
            golden = json.load(f)
        admin = StatuteLinkConverterAdmin(model=StatuteLinkConverter, admin_site=None)
        conversions, failures = admin.try_import("http://test.com/test.xml", "Social Security Act")
        all = conversions + failures
        for i in all:
            del i["id"]
        # Despite the name, assertCountEqual does make sure all items in the list are the same, not just the count.
        # It just supports lists that are out of order, unlike assertEqual.
        self.assertCountEqual(all, golden)

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_try_import_multiple_titles(self, mocked_get):
        with open("regulations/tests/fixtures/statute_link_golden_aca.json", "r") as f:
            golden = json.load(f)
        admin = StatuteLinkConverterAdmin(model=StatuteLinkConverter, admin_site=None)
        conversions, failures = admin.try_import("http://test.com/test_aca.xml", "Affordable Care Act")
        all = conversions + failures
        for i in all:
            del i["id"]
        # Despite the name, assertCountEqual does make sure all items in the list are the same, not just the count.
        # It just supports lists that are out of order, unlike assertEqual.
        self.assertCountEqual(all, golden)

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_try_import_404(self, mocked_get):
        admin = StatuteLinkConverterAdmin(model=StatuteLinkConverter, admin_site=None)
        with self.assertRaises(HTTPError):
            _ = admin.try_import("http://test.com/bad-link.xml", "Social Security Act")

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_try_import_conversions_exist(self, mocked_get):
        with open("regulations/tests/fixtures/statute_link_golden.json", "r") as f:
            golden = json.load(f)
        for i in golden:
            StatuteLinkConverter.objects.create(**i)
        admin = StatuteLinkConverterAdmin(model=StatuteLinkConverter, admin_site=None)
        with self.assertRaises(ValidationError):
            _ = admin.try_import("http://test.com/test.xml", "Social Security Act")

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_try_import_no_conversions(self, mocked_get):
        admin = StatuteLinkConverterAdmin(model=StatuteLinkConverter, admin_site=None)
        with self.assertRaises(ValidationError):
            _ = admin.try_import("http://test.com/invalid.xml", "Social Security Act")

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_try_import_bad_params(self, mocked_get):
        admin = StatuteLinkConverterAdmin(model=StatuteLinkConverter, admin_site=None)
        bad_params = [
            ("", "SSA"),
            ("  ", "SSA"),
            ("http://test.com/test.xml", ""),
        ]
        for i in bad_params:
            self.assertRaises(ValidationError, admin.try_import, *i)


class LinkStatutesTestCase(SimpleTestCase):

    def test_link_statutes(self):
        link_conversions = {
            "Social Security Act": {
                "123": {
                    "title": "42",
                    "usc": "abc",
                },
                "456": {
                    "title": "43",
                    "usc": "def",
                },
            },
            "Affordable Care Act": {
                "789": {
                    "title": "44",
                    "usc": "xyz",
                },
            },
        }

        with open("regulations/tests/fixtures/section_link_tests.json", "r") as f:
            test_values = json.load(f)

        for test in test_values:
            template = Template("{% load link_statutes %}{{ paragraph|link_statutes:link_conversions|safe }}")
            context = Context({"paragraph": test["input"], "link_conversions": link_conversions})
            self.assertEqual(template.render(context), test["expected"], f"Failed while testing {test['testing']}.")


class StatuteConvertersAPITestCase(APITestCase):
    def setUp(self):
        with open("regulations/tests/fixtures/statute_link_api_test.json", "r") as f:
            self.objects = json.load(f)
            for i in self.objects:
                StatuteLinkConverter.objects.create(**i)

    def test_all_statutes(self):
        response = self.client.get("/v3/statutes")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data, self.objects)

    def test_aca(self):
        response = self.client.get("/v3/statutes?act=Affordable Care Act")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data, self.objects[0:1])

    def test_ssa(self):
        response = self.client.get("/v3/statutes?act=Social Security Act")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data, self.objects[1:3])
