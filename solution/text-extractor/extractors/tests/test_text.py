from . import FixtureTestCase


class TestTextExtractor(FixtureTestCase):
    def test_extract_utf8(self):
        self._test_file_type("txt", variation="utf8")

    def test_extract_win_1252(self):
        self._test_file_type("txt", variation="w1252")

    def test_extract_iso_8859_1(self):
        self._test_file_type("txt", variation="iso8859-1")

    # TODO: Enable this test when Magika is updated to support UTF-16 files.
    # This file type is not urgently needed.
    # def test_extract_utf16(self):
    #     self._test_file_type("txt", variation="utf16")
