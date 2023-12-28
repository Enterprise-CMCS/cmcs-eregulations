import unittest

from extractors import Extractor, ExtractorInitException


class TestExtractor(Extractor):
    file_types = ("type1", "type2")


class ExtractorTest(unittest.TestCase):
    def test_get_extractor(self):
        extractor = Extractor.get_extractor("type2")
        self.assertIsInstance(extractor, TestExtractor)

        extractor = Extractor.get_extractor("type2")
        self.assertIsInstance(extractor, TestExtractor)

    def test_no_extractor(self):
        with self.assertRaises(ExtractorInitException):
            Extractor.get_extractor("badtype")

    def test_no_extract_function(self):
        with self.assertRaises(NotImplementedError):
            extractor = Extractor.get_extractor("type1")
            file = "hello world.txt"
            extractor.extract(file)
