import unittest

from extractors import (
    ExcelExtractor,
    Extractor,
)

from . import FileComparisonMixin


class TestExcelExtractor(unittest.TestCase, FileComparisonMixin):
    def test_create(self):
        for i in ExcelExtractor.file_types:
            extractor = Extractor.get_extractor(i)
            self.assertIsInstance(extractor, ExcelExtractor)

    def test_xls(self):
        self._test_file_type("xls")

    def test_xlsx(self):
        self._test_file_type("xlsx")

    def test_xlsm(self):
        self._test_file_type("xlsm")
