import unittest

from extractors import (
    Extractor,
    WordExtractor,
)

from . import FileComparisonMixin


class TestWordExtractor(unittest.TestCase, FileComparisonMixin):
    def test_create(self):
        for i in WordExtractor.file_types:
            extractor = Extractor.get_extractor(i)
            self.assertIsInstance(extractor, WordExtractor)

    def test_docx(self):
        self._test_file_type("docx")
