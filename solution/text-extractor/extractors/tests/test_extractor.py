import unittest

from extractors import Extractor, ExtractorInitException


class TestExtractor(Extractor):
    file_types = ("sample/mimetype1", "sample/mimetype2")


class ExtractorTest(unittest.TestCase):
    def test_get_extractor(self):
        extractor = Extractor.get_extractor("sample/mimetype1")
        self.assertIsInstance(extractor, TestExtractor)

        extractor = Extractor.get_extractor("sample/mimetype2")
        self.assertIsInstance(extractor, TestExtractor)

    def test_no_extractor(self):
        with self.assertRaises(ExtractorInitException):
            Extractor.get_extractor("unregistered/mimetype")

    def test_no_extract_function(self):
        with self.assertRaises(NotImplementedError):
            extractor = Extractor.get_extractor("sample/mimetype1")
            file = b'hello world'
            extractor.extract(file)
