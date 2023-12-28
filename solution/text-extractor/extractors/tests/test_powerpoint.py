import unittest

from extractors import (
    Extractor,
    PowerPointExtractor,
)

from . import FileComparisonMixin


class TestPowerPointExtractor(unittest.TestCase, FileComparisonMixin):
    def test_create(self):
        for i in PowerPointExtractor.file_types:
            extractor = Extractor.get_extractor(i)
            self.assertIsInstance(extractor, PowerPointExtractor)

    def test_pptx(self):
        self._test_file_type("pptx")
