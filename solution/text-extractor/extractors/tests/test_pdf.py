from unittest.mock import patch


from extractors import (
    Extractor,
    ExtractorException,
    PdfExtractor,
)

from . import FixtureTestCase

orig = Extractor.get_extractor


class MockJpegExtractor:
    def extract(self, file: bytes) -> str:
        if Extractor.get_file_type(file) != "jpeg":
            raise ExtractorException("Extractor did not convert page to jpeg.")
        return "Sample output"  # Expected file will contain 2 copies of this as there are 2 pages in the PDF


class MockNullExtractor:
    def extract(self, file: bytes) -> str:
        return "Sample output"


def mock_get_extractor(file_type: str, config: dict = {}) -> Extractor:
    if file_type == "jpeg":
        return MockJpegExtractor()
    if file_type == "null":
        return MockNullExtractor()
    return orig(file_type, config)


def mock_convert_to_images(self: PdfExtractor, file: bytes, temp_dir: str) -> [str]:
    for i in range(self.max_pages + 10):
        with open(f"{temp_dir}/page{i}.null", "wb") as f:
            f.write(b"null")
    return [f"{temp_dir}/page{i}.null" for i in range(self.max_pages + 10)]


class TestPdfExtractor(FixtureTestCase):
    # This simple test verifies that multipage support is working and that it is converting PDF pages to jpeg images.
    @patch.object(Extractor, "get_extractor", mock_get_extractor)
    def test_extract_pdf(self):
        self._test_file_type("pdf")

    # This test verifies that the extractor will only extract up to the maximum number of pages.
    @patch.object(Extractor, "get_extractor", mock_get_extractor)
    @patch.object(PdfExtractor, "_convert_to_images", mock_convert_to_images)
    def test_pdf_max_pages(self, *args):
        with open(f"{self.BASE_PATH}pdf/sample.pdf", "rb") as f:
            sample = f.read()
        output = PdfExtractor("pdf", {}, output_file_type="null").extract(sample)
        self.assertEqual(output.count("Sample output"), PdfExtractor.max_pages)
