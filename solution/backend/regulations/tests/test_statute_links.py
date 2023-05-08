import json
from unittest import mock

from django.core.exceptions import ValidationError
from django.template import Context, Template
from django.test import TestCase
from django.test import SimpleTestCase

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
    elif args[0] == "http://test.com/invalid.xml":
        return MockResponse(200, "Hello World")
    return MockResponse(404, "invalid URL")


class TestStatuteLinkImport(TestCase):
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_try_import(self, mocked_get):
        with open("regulations/tests/fixtures/statute_link_golden.json", "r") as f:
            golden = json.load(f)
        admin = StatuteLinkConverterAdmin(model=StatuteLinkConverter, admin_site=None)
        conversions = admin.try_import("http://test.com/test.xml", "SSA")
        # Despite the name, assertCountEqual does make sure all items in the list are the same, not just the count.
        # It just supports lists that are out of order, unlike assertEqual.
        self.assertCountEqual(conversions, golden)

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_try_import_404(self, mocked_get):
        admin = StatuteLinkConverterAdmin(model=StatuteLinkConverter, admin_site=None)
        with self.assertRaises(HTTPError):
            _ = admin.try_import("http://test.com/bad-link.xml", "SSA")

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_try_import_conversions_exist(self, mocked_get):
        with open("regulations/tests/fixtures/statute_link_golden.json", "r") as f:
            golden = json.load(f)
        for i in golden:
            StatuteLinkConverter.objects.create(
                title=i["title"],
                section=i["section"],
                usc=i["usc"],
                act=i["act"],
                source_url=i["source_url"]
            )
        admin = StatuteLinkConverterAdmin(model=StatuteLinkConverter, admin_site=None)
        with self.assertRaises(ValidationError):
            _ = admin.try_import("http://test.com/test.xml", "SSA")

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_try_import_no_conversions(self, mocked_get):
        admin = StatuteLinkConverterAdmin(model=StatuteLinkConverter, admin_site=None)
        with self.assertRaises(ValidationError):
            _ = admin.try_import("http://test.com/invalid.xml", "SSA")

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
            "123": {
                "usc": "abc",
                "title": "42",
                "act": "Social Security Act",
            },
            "456": {
                "usc": "def",
                "title": "43",
                "act": "Social Security Act",
            },
            "789": {
                "usc": "xyz",
                "title": "44",
                "act": "Affordable Care Act",
            },
        }

        test_values = [
            {
                "input": "Section 123(a) of the Act",
                "expected": 'Section <a target="_blank" href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-'
                            'sectionabc&num=0&edition=prelim">123(a)</a> of the Act',
            },
            {
                "input": "section 123(a)(1)(C) and 456(b)(2) of the Social Security Act",
                "expected": 'section <a target="_blank" href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-sectionabc&num=0&edition=prelim">123(a)(1)(C)</a> and <a target="_blank" href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title43-sectiondef&num=0&edition=prelim">456(b)(2)</a> of the Social Security Act',
            },
            {
                "input": "section 123(a)(1)(C), (b)(1), and (b)(2) of the act",
                "expected": 'section <a target="_blank" href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-sectionabc&num=0&edition=prelim">123(a)(1)(C), (b)(1), and (b)(2)</a> of the act',
            },
            {
                "input": "sections 123(a)(1)(C), (b)(1), and (b)(2) and 456(a)(1) and (b)(1) and 456(f) or (g) of the act",
                "expected": 'sections <a target="_blank" href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-sectionabc&num=0&edition=prelim">123(a)(1)(C), (b)(1), and (b)(2)</a> and <a target="_blank" href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title43-sectiondef&num=0&edition=prelim">456(a)(1) and (b)(1)</a> and <a target="_blank" href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title43-sectiondef&num=0&edition=prelim">456(f) or (g)</a> of the act'
            }
        ]

        for test in test_values:
            template = Template("{% load link_statutes %}{{ paragraph|link_statutes:link_conversions|safe }}")
            context = Context({"paragraph": test["input"], "link_conversions": link_conversions})
            self.assertEqual(template.render(context), test["expected"])

