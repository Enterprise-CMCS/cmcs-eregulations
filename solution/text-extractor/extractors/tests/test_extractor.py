import unittest
from unittest.mock import patch

from extractors import (
    Extractor,
    ExtractorException,
    ExtractorInitException,
)


class TestExtractor(Extractor):
    file_types = ("type1", "type2")


class WriteFileExtractor(Extractor):
    file_types = ("type3",)

    def extract(self, file: bytes) -> str:
        file_path = self._write_file(file)
        with open(file_path, "rb") as f:
            data = f.read()
        return data.decode()


class EmbeddedFileExtractor(Extractor):
    file_types = ("type4",)

    def extract(self, file: bytes) -> str:
        return file.decode()


class EmbeddedFileExtractorExpectedFailure(Extractor):
    file_types = ("type5",)

    def extract(self, file: bytes) -> str:
        raise ExtractorException("Failed to extract")


class EmbeddedFileExtractorUnexpectedFailure(Extractor):
    file_types = ("type6",)

    def extract(self, file: bytes) -> str:
        raise TypeError()


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

    def test_write_file(self):
        file = b"This is a file"
        extractor = Extractor.get_extractor("type3")
        text = extractor.extract(file)
        self.assertEqual(text, file.decode())

    @patch.object(Extractor, "_get_mime_type", return_value="type4")
    def test_extract_embedded_success(self, *args):
        file = b"This is a file"
        file_name = "file.type4"
        extractor = Extractor.get_extractor("type1")
        output = extractor._extract_embedded(file_name, file)
        self.assertEqual(output, file.decode())

    @patch.object(Extractor, "_get_mime_type", return_value="type1000")
    def test_extract_embedded_invalid_type(self, *args):
        file = b"This is a file"
        file_name = "file.type1000"
        extractor = Extractor.get_extractor("type1")
        output = extractor._extract_embedded(file_name, file)
        self.assertEqual(output, "")

    @patch.object(Extractor, "_get_mime_type", return_value="type5")
    def test_extract_embedded_extract_failure(self, *args):
        file = b"This is a file"
        file_name = "file.type5"
        extractor = Extractor.get_extractor("type1")
        output = extractor._extract_embedded(file_name, file)
        self.assertEqual(output, "")

    @patch.object(Extractor, "_get_mime_type", return_value="type6")
    def test_extract_embedded_unexpected_failure(self, *args):
        file = b"This is a file"
        file_name = "file.type6"
        extractor = Extractor.get_extractor("type1")
        output = extractor._extract_embedded(file_name, file)
        self.assertEqual(output, "")
