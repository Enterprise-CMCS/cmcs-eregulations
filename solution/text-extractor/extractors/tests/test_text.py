import unittest

import extractors


class TestTextExtractor(unittest.TestCase):
    def test_create(self):
        extractor = extractors.Extractor.get_extractor("text/plain")
        self.assertIsInstance(extractor, extractors.TextExtractor)

    def test_extract(self):
        extractor = extractors.Extractor.get_extractor("text/plain")
        output = extractor.extract(b"This is plain text")
        self.assertEqual(output, "This is plain text")
