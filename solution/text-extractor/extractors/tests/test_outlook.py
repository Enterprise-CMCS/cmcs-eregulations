from . import FixtureTestCase


class TestOutlookExtractor(FixtureTestCase):
    def test_msg(self):
        self._test_file_type("msg")
