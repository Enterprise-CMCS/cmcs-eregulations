import unittest

from extractors import Extractor, PdfExtractor


class TestPdfExtractor(unittest.TestCase):
    def test_create(self):
        extractor = Extractor.get_extractor("application/pdf")
        self.assertIsInstance(extractor, extractors.PdfExtractor)

    def test_extract(self):
        extractor = extractors.Extractor.get_extractor("text/plain")
        output = extractor.extract(b"This is plain text")
        self.assertEqual(output, "This is plain text")
