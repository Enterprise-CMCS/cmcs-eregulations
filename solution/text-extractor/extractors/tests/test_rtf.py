import unittest

import extractors

from . import FileComparisonMixin


class TestRichTextExtractor(unittest.TestCase, FileComparisonMixin):
    def test_create(self):
        extractor = extractors.Extractor.get_extractor("rtf")
        self.assertIsInstance(extractor, extractors.RichTextExtractor)

    def test_extract_rtf(self):
        self._test_file_type("rtf")

    def test_extract_rtf_corrupt(self):
        self._test_file_type("rtf", variation="corrupt")
