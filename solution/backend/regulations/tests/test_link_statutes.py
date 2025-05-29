# File: test_link_statutes.py
from unittest.mock import MagicMock

from django.test import TestCase

from regulations.utils.link_statutes import replace_section, replace_usc_citation


class ReplaceCitationTests(TestCase):
    def setUp(self):
        # Common setup for tests
        self.maxDiff = None  # To see full diff in case of failure
        self.exceptions = {"42": ["1901"]}
        self.link_conversions = {
            "Social Security Act": {
                "1902": {"title": "42", "usc": "1902"}
            }
        }

    def test_replace_usc_citation_generate_url_only_false(self):
        match = MagicMock()
        match.group.side_effect = ["6409"]
        result = replace_usc_citation(match, title="42", exceptions=self.exceptions, generate_url_only=False)
        expected_link = (
            '<a target="_blank" rel="noopener noreferrer" class="external" '
            'href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section6409&num=0&edition=prelim">'
            '6409</a>'
        )
        self.assertEqual(result, expected_link)

    def test_replace_usc_citation_generate_url_only_true(self):
        match = MagicMock()
        match.group.side_effect = ["6409"]
        result = replace_usc_citation(match, title="42", exceptions=self.exceptions, generate_url_only=True)
        expected_link = (
            "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section6409&num=0&edition=prelim"
        )
        self.assertEqual(result, expected_link)

    def test_replace_section_generate_url_only_false(self):
        match = MagicMock()
        match.group.side_effect = ["1102"]
        link_conversions_mock = {
            "Social Security Act": {
                "1102": {"title": "42", "usc": "1302"}
            }
        }
        result = replace_section(
            match, act="Social Security Act", link_conversions=link_conversions_mock, exceptions=[], generate_url_only=False
        )
        expected_link = (
            '<a target="_blank" rel="noopener noreferrer" class="external" '
            'href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1302&num=0&edition=prelim">'
            '1102</a>'
        )
        self.assertEqual(result, expected_link)

    def test_replace_section_generate_url_only_true(self):
        match = MagicMock()
        match.group.side_effect = ["1102"]
        link_conversions_mock = {
            "Social Security Act": {
                "1102": {"title": "42", "usc": "1302"}
            }
        }
        result = replace_section(
            match,
            act="Social Security Act", link_conversions=link_conversions_mock, exceptions=self.exceptions, generate_url_only=True
        )
        expected_link = (
            "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1302&num=0&edition=prelim"
        )
        self.assertEqual(result, expected_link)
