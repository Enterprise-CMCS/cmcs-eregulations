
import unittest

from extractors import (
    BinaryExtractor,
    Extractor,
)

from . import FileComparisonMixin


class TestOfficeExtractor(unittest.TestCase, FileComparisonMixin):
    def test_create(self):
        self.assertIsInstance(Extractor.get_extractor("doc"), BinaryExtractor)

    def test_extract(self):
        self._test_file_type("doc")
