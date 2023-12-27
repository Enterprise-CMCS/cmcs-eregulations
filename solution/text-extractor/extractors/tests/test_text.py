import unittest

import extractors

from . import FileComparisonMixin


class TestTextExtractor(unittest.TestCase, FileComparisonMixin):
    def test_create(self):
        extractor = extractors.Extractor.get_extractor("txt")
        self.assertIsInstance(extractor, extractors.TextExtractor)

    def test_extract(self):
        self._test_file_type("txt")
