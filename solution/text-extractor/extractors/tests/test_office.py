import unittest

from extractors import (
    Extractor,
    ExtractorException,
    OfficeExtractor,
)


class TestOfficeExtractor(unittest.TestCase): 
    def _test_file_type(self, file_type):
        extractor = Extractor.get_extractor(file_type)
        output = extractor.extract(f"extractors/tests/fixtures/{file_type}_sample.{file_type}")
        with open(f"extractors/tests/fixtures/{file_type}_expected.txt", "r") as f:
            expected = f.read()
        self.assertEqual(output, expected)

    def test_create(self):
        for i in OfficeExtractor.file_types:
            extractor = Extractor.get_extractor(i)
            self.assertIsInstance(extractor, OfficeExtractor)

    def test_xls(self):
        self._test_file_type("xls")

    def test_xlsx(self):
        self._test_file_type("xlsx")

    def test_docx(self):
        self._test_file_type("docx")
