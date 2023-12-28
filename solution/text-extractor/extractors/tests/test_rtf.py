import unittest

import extractors

from . import FileComparisonMixin


class TestRichTextExtractor(unittest.TestCase, FileComparisonMixin):
    def test_extract_rtf(self):
        self._test_file_type("rtf")

    def test_extract_rtf_corrupt(self):
        self._test_file_type("rtf", variation="corrupt")
