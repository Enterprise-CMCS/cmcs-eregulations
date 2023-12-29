from . import FixtureTestCase


class TestOldExcelExtractor(FixtureTestCase):
    def test_xls(self):
        self._test_file_type("xls")
