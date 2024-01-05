import unittest

import extractors

from . import FileComparisonMixin


class TestTextExtractor(unittest.TestCase, FileComparisonMixin):
    def test_create(self):
        extractor = extractors.Extractor.get_extractor("txt")
        self.assertIsInstance(extractor, extractors.TextExtractor)

    def test_extract_utf8(self):
        self._test_file_type("txt", variation="utf8")

    def test_extract_win_1252(self):
        self._test_file_type("txt", variation="w1252")

    def test_extract_iso_8859_1(self):
        self._test_file_type("txt", variation="iso8859-1")

    def test_extract_utf16(self):
        self._test_file_type("txt", variation="utf16")
