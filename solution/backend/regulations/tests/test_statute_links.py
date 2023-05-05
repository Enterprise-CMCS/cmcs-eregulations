import json
from unittest import mock
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase

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


from regulations.templatetags.link_statutes import extract_sections, link_statutes


class TestExtractSections(unittest.TestCase):
    
    def test_simple_sections(self):
        text = "This is a test section 1(a)(1) and section 2(b) of the act."
        expected = [
            {
                "text": "1(a)(1)",
                "section": "1",
                "paragraphs": [["a", "1"]]
            },
            {
                "text": "2(b)",
                "section": "2",
                "paragraphs": [["b"]]
            }
        ]
        self.assertEqual(extract_sections(text), expected)

    def test_complex_sections(self):
        text = "This is a test section 123(a)(1)(C)(i), (ii), and (iii) and 456(b)(2)(D)(1), (2), and (3) of the act."
        expected = [
            {
                "text": "123(a)(1)(C)(i), (ii), and (iii)",
                "section": "123",
                "paragraphs": [
                    ["a", "1", "C", "i"],
                    ["ii"],
                    ["iii"],
                ]
            },
            {
                "text": "456(b)(2)(D)(1), (2), and (3)",
                "section": "456",
                "paragraphs": [
                    ["b", "2", "D", "1"],
                    ["2"],
                    ["3"],
                ]
            }
        ]
        self.assertEqual(extract_sections(text), expected)


class TestLinkStatutes(unittest.TestCase):
    
    def setUp(self):
        self.link_conversions = {
            "123": {
                "title": "42",
                "usc": "789A",
            },
            "456": {
                "title": "43",
                "usc": "987B",
            },
        }

    def test_link_statutes(self):
        paragraph = "This is a test 123 and 456."
        expected = 'This is a test <a target="_blank" href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-titleTitle1-section123&num=0&edition=prelim">123</a> and <a target="_blank" href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-titleTitle2-section456&num=0&edition=prelim">456</a>.'
        self.assertEqual(link_statutes(paragraph, self.link_conversions), expected)

    def test_link_statutes_no_match(self):
        paragraph = "This is a test without any statute reference."
        expected = "This is a test without any statute reference."
        self.assertEqual(link_statutes(paragraph, self.link_conversions), expected)

    def test_link_statutes_with_wrong_conversions(self):
        paragraph = "This is a test 123 and 456."
        wrong_conversions = {
            "456": {
                "title": "Title1",
                "usc": "789",
            },
        }
        expected = 'This is a test <a target="_blank" href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-titleTitle1-section123&num=0&edition=prelim">123</a> and 456.'
        self.assertEqual(link_statutes(paragraph, wrong_conversions), expected)

    @patch("your_module.extract_sections", return_value=[])
    def test_link_statutes_extract_sections_not_called(self, mock_extract_sections):
        paragraph = "This is a test 123 and 456."
        expected = 'This is a test 123 and 456.'
        self.assertEqual(link_statutes(paragraph, self.link_conversions), expected)
        mock_extract_sections.assert_not_called()

    @patch("your_module.extract_sections", return_value=[{"text": "123(a)", "section": "123", "paragraphs": [["a"]]}])
    def test_link_statutes_single_section_linked(self, mock_extract_sections):
        paragraph = "This is a test 123(a)."
        expected = '<a target="_blank" href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-titleTitle1-section123&num=0&edition=prelim">123(a)</a>.'
