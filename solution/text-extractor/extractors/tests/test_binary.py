
import unittest

from extractors import (
    Extractor,
    BinaryExtractor,
)


class TestOfficeExtractor(unittest.TestCase):
    def test_create(self):
        self.assertIsInstance(Extractor.get_extractor("doc"), BinaryExtractor)

    def test_extract(self):
        with open("extractors/tests/fixtures/doc_expected.txt", "r") as f:
            expected = f.read()
        extractor = Extractor.get_extractor("doc")
        output = extractor.extract("extractors/tests/fixtures/doc_sample.doc")
        self.assertEqual(output, expected)
