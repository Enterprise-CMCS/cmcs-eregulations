from . import FixtureTestCase


class TestWordExtractor(FixtureTestCase):
    def test_docx(self):
        self._test_file_type("docx")
