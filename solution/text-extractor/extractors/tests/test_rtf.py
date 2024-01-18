from . import FixtureTestCase


class TestRichTextExtractor(FixtureTestCase):
    def test_extract_rtf(self):
        self._test_file_type("rtf")

    def test_extract_rtf_corrupt(self):
        self._test_file_type("rtf", variation="corrupt")
