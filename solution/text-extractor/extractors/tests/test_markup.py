import unittest

from . import FileComparisonMixin


class TestMarkupExtractor(unittest.TestCase, FileComparisonMixin):
    def test_extract_html(self):
        self._test_file_type("html")

    def test_extract_htm(self):
        self._test_file_type("htm")

    def test_extract_xhtml(self):
        self._test_file_type("xhtml")

    def test_extract_xml(self):
        self._test_file_type("xml")
