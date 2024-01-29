from unittest.mock import patch

import magic

from extractors import (
    Extractor,
    ExtractorException,
)

from . import FixtureTestCase

orig = Extractor.get_extractor


class MockJpegExtractor:
    def extract(self, file: bytes) -> str:
        if magic.from_buffer(file[:2048], mime=True) != "image/jpeg":
            raise ExtractorException("Extractor did not convert to jpeg.")
        return "Sample output"


def mock_get_extractor(file_type: str, config: dict = {}) -> Extractor:
    if file_type == "jpeg":
        return MockJpegExtractor()
    return orig(file_type, config)


class TestImageExtractor(FixtureTestCase):
    def test_extract_gif(self):
        with patch("extractors.Extractor.get_extractor", new=mock_get_extractor):
            self._test_file_type("gif", collection="images")

    def test_extract_j2k(self):
        with patch("extractors.Extractor.get_extractor", new=mock_get_extractor):
            self._test_file_type("j2k", collection="images")

    def test_extract_jp2(self):
        with patch("extractors.Extractor.get_extractor", new=mock_get_extractor):
            self._test_file_type("jp2", collection="images")

    def test_extract_jpx(self):
        with patch("extractors.Extractor.get_extractor", new=mock_get_extractor):
            self._test_file_type("jpx", collection="images")

    def test_extract_bmp(self):
        with patch("extractors.Extractor.get_extractor", new=mock_get_extractor):
            self._test_file_type("bmp", collection="images")

    def test_extract_tga(self):
        with patch("extractors.Extractor.get_extractor", new=mock_get_extractor):
            self._test_file_type("tga", collection="images")

    def test_extract_webp(self):
        with patch("extractors.Extractor.get_extractor", new=mock_get_extractor):
            self._test_file_type("webp", collection="images")