import unittest

from . import FileComparisonMixin


class TestOldExcelExtractor(unittest.TestCase, FileComparisonMixin):
    def test_xls(self):
        self._test_file_type("xls")
