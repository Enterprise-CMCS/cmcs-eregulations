import unittest

from extractors import (
    Extractor,
    OutlookExtractor,
)

from . import FileComparisonMixin


class TestOutlookExtractor(unittest.TestCase, FileComparisonMixin):
    def test_create(self):
        for i in OutlookExtractor.file_types:
            extractor = Extractor.get_extractor(i)
            self.assertIsInstance(extractor, OutlookExtractor)

    def test_msg(self):
        self._test_file_type("msg")
