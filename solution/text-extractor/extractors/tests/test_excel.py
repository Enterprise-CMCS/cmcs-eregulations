from . import FixtureTestCase


class TestExcelExtractor(FixtureTestCase):
    def test_xlsx(self):
        self._test_file_type("xlsx")

    def test_xlsm(self):
        self._test_file_type("xlsm")
