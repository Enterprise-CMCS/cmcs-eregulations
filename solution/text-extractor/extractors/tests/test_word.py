import unittest

from extractors import (
    Extractor,
    WordExtractor,
)

from . import FileComparisonMixin


class TestWordExtractor(unittest.TestCase, FileComparisonMixin):
    def test_docx(self):
        self._test_file_type("docx")
