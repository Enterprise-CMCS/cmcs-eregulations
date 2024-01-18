from . import FixtureTestCase


class TestEmailExtractor(FixtureTestCase):
    def test_extract(self):
        self._test_file_type("eml")
