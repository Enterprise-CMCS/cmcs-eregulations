from unittest.mock import patch

from magika import Magika

from extractors import (
    Extractor,
    ExtractorException,
)

from . import FixtureTestCase

orig = Extractor.get_extractor


class MockJpegExtractor:
    def extract(self, file: bytes) -> str:
        if Magika().identify_bytes(file).output.mime_type != "image/jpeg":
            raise ExtractorException("Extractor did not convert page to jpeg.")
        return "Sample output"  # Expected file will contain 2 copies of this as there are 2 pages in the PDF


def mock_get_extractor(file_type: str, config: dict = {}) -> Extractor:
    if file_type == "jpeg":
        return MockJpegExtractor()
    return orig(file_type, config)


# This simple test verifies that multipage support is working and that it is converting PDF pages to jpeg images.
class TestPdfExtractor(FixtureTestCase):
    @patch.object(Extractor, "get_extractor", mock_get_extractor)
    def test_extract_pdf(self):
        self._test_file_type("pdf")
