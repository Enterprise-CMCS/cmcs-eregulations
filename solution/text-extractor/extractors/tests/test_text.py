import unittest
from tempfile import TemporaryDirectory
import os

import extractors


class TestTextExtractor(unittest.TestCase):
    def test_create(self):
        extractor = extractors.Extractor.get_extractor("text/plain")
        self.assertIsInstance(extractor, extractors.TextExtractor)

    def test_extract(self):
        extractor = extractors.Extractor.get_extractor("text/plain")
        with TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "sample.txt")
            with open(path, "w") as f:
                f.write("This is plain text")
            output = extractor.extract(path)
            self.assertEqual(output, "This is plain text")
