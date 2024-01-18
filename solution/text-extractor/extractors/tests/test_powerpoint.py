from . import FixtureTestCase


class TestPowerPointExtractor(FixtureTestCase):
    def test_pptx(self):
        self._test_file_type("pptx")
