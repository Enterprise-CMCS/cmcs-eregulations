from . import FixtureTestCase


class TestZipExtractor(FixtureTestCase):
    def test_extract(self):
        self._test_file_type("zip")
