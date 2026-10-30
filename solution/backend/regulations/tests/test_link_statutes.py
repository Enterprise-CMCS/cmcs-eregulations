# File: test_link_statutes.py
from unittest.mock import MagicMock

from django.test import TestCase

from regulations.utils.link_statutes import replace_section, replace_usc_citation


class ReplaceCitationTests(TestCase):
    def setUp(self):
        # Common setup for tests
        self.maxDiff = None  # To see full diff in case of failure
        self.link_conversions = {
            "Social Security Act": {
                "1102": {"title": "42", "usc": "1302"}
            }
        }

    def test_replace_usc_citation_exception_url_only_false(self):
        match = MagicMock()
        match.group.side_effect = ["6409"]
        mock_usc_ref_exceptions = {"26": ["6409"]}
        mock_title = "26"
        mock_exceptions = mock_usc_ref_exceptions.get(mock_title, [])
        result = replace_usc_citation(
            match, title=mock_title, exceptions=mock_exceptions, generate_url_only=False
        )
        self.assertEqual(result, "6409")

    def test_replace_usc_citation_exception_url_only_true(self):
        match = MagicMock()
        match.group.side_effect = ["6409"]
        mock_usc_ref_exceptions = {"26": ["6409"]}
        mock_title = "26"
        mock_exceptions = mock_usc_ref_exceptions.get(mock_title, [])
        result = replace_usc_citation(
            match, title=mock_title, exceptions=mock_exceptions, generate_url_only=True
        )
        self.assertEqual(result, "")

    def test_replace_usc_citation_generate_url_only_false(self):
        match = MagicMock()
        match.group.side_effect = ["6409"]
        result = replace_usc_citation(match, title="42", exceptions={}, generate_url_only=False)
        expected_link = (
            '<a target="_blank" rel="noopener noreferrer" class="external" '
            'href="https://uscode.house.gov/us/usc/t42/s6409">6409</a>'
        )
        self.assertEqual(result, expected_link)

    def test_replace_usc_citation_generate_url_only_true(self):
        match = MagicMock()
        match.group.side_effect = ["6409"]
        result = replace_usc_citation(match, title="42", exceptions={}, generate_url_only=True)
        expected_link = "https://uscode.house.gov/us/usc/t42/s6409"
        self.assertEqual(result, expected_link)

    def test_replace_usc_citation_with_paragraphs_omits_fragment(self):
        match = MagicMock()
        match.group.side_effect = ["6409(a)(1)"]
        result = replace_usc_citation(match, title="42", exceptions={}, generate_url_only=True)
        self.assertEqual(result, "https://uscode.house.gov/us/usc/t42/s6409")

    def test_replace_section_exception_url_only_false(self):
        match = MagicMock()
        match.group.side_effect = ["1102"]
        mock_act = "Social Security Act"
        mock_statute_ref_exceptions = {"Social Security Act": ["1102"]}
        mock_exceptions = mock_statute_ref_exceptions.get(mock_act, [])
        result = replace_section(
            match, act=mock_act, link_conversions=self.link_conversions, exceptions=mock_exceptions, generate_url_only=False
        )
        self.assertEqual(result, "1102")

    def test_replace_section_exception_url_only_true(self):
        match = MagicMock()
        match.group.side_effect = ["1102"]
        mock_act = "Social Security Act"
        mock_statute_ref_exceptions = {"Social Security Act": ["1102"]}
        mock_exceptions = mock_statute_ref_exceptions.get(mock_act, [])
        result = replace_section(
            match, act=mock_act, link_conversions=self.link_conversions, exceptions=mock_exceptions, generate_url_only=True
        )
        self.assertEqual(result, "")

    def test_replace_section_generate_url_only_false(self):
        match = MagicMock()
        match.group.side_effect = ["1102"]
        result = replace_section(
            match, act="Social Security Act", link_conversions=self.link_conversions, exceptions={}, generate_url_only=False
        )
        expected_link = (
            '<a target="_blank" rel="noopener noreferrer" class="external" '
            'href="https://uscode.house.gov/us/usc/t42/s1302">1102</a>'
        )
        self.assertEqual(result, expected_link)

    def test_replace_section_generate_url_only_true(self):
        match = MagicMock()
        match.group.side_effect = ["1102"]
        result = replace_section(
            match,
            act="Social Security Act", link_conversions=self.link_conversions, exceptions={}, generate_url_only=True
        )
        expected_link = "https://uscode.house.gov/us/usc/t42/s1302"
        self.assertEqual(result, expected_link)

    def test_replace_section_with_paragraphs_omits_fragment(self):
        match = MagicMock()
        match.group.side_effect = ["1102(a)(1)"]
        result = replace_section(
            match,
            act="Social Security Act", link_conversions=self.link_conversions, exceptions={}, generate_url_only=True
        )
        self.assertEqual(result, "https://uscode.house.gov/us/usc/t42/s1302")
