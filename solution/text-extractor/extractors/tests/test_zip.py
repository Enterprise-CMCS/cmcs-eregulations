import unittest

from . import FileComparisonMixin


class TestTextExtractor(unittest.TestCase, FileComparisonMixin):
    def test_extract(self):
        self._test_file_type("zip")
