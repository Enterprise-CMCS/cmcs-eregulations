import unittest

from . import FileComparisonMixin


class TestOutlookExtractor(unittest.TestCase, FileComparisonMixin):
    def test_msg(self):
        self._test_file_type("msg")
