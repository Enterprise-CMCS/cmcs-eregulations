from . import FixtureTestCase


class TestBinaryExtractor(FixtureTestCase):
    def test_extract(self):
        self._test_file_type("doc")
