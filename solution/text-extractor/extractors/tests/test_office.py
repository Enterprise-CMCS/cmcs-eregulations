import unittest

from extractors import (
    Extractor,
    OfficeExtractor,
)

from . import FileComparisonMixin


class TestOfficeExtractor(unittest.TestCase, FileComparisonMixin):
    def test_create(self):
        for i in OfficeExtractor.file_types:
            extractor = Extractor.get_extractor(i)
            self.assertIsInstance(extractor, OfficeExtractor)

    def test_pptx(self):
        self._test_file_type("pptx")
