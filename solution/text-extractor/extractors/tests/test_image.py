from unittest.mock import patch


from extractors import (
    Extractor,
    ExtractorException,
)

from . import FixtureTestCase

orig = Extractor.get_extractor


class MockJpegExtractor:
    def extract(self, file: bytes) -> str:
        if Extractor.get_file_type(file) != "jpeg":
            raise ExtractorException("Extractor did not convert to jpeg.")
        return "Sample output"


def mock_get_extractor(file_type: str, config: dict = {}) -> Extractor:
    if file_type == "jpeg":
        return MockJpegExtractor()
    return orig(file_type, config)


class TestImageExtractor(FixtureTestCase):
    @patch.object(Extractor, "get_extractor", mock_get_extractor)
    def test_extract_gif(self):
        self._test_file_type("gif", collection="images")

    @patch.object(Extractor, "get_extractor", mock_get_extractor)
    def test_extract_bmp(self):
        self._test_file_type("bmp", collection="images")

    @patch.object(Extractor, "get_extractor", mock_get_extractor)
    def test_extract_tga(self):
        self._test_file_type("tga", collection="images")

    @patch.object(Extractor, "get_extractor", mock_get_extractor)
    def test_extract_webp(self):
        self._test_file_type("webp", collection="images")
