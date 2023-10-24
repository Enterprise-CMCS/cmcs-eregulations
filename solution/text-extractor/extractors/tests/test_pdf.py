import unittest
from unittest.mock import patch

import botocore
import magic

from extractors import (
    Extractor,
    ExtractorException,
    PdfExtractor,
)

# Original botocore _make_api_call function
orig = botocore.client.BaseClient._make_api_call


# Mocked botocore _make_api_call function
def mock_make_api_call(self, operation_name, kwarg):
    if operation_name == 'DetectDocumentText':
        doc = kwarg["Document"]["Bytes"]
        file_type = magic.from_buffer(doc[:2048], mime=True)
        if file_type != "image/jpeg":
            raise Exception("Did not convert to JPEG!")
        return {
            "Blocks": [
                {
                    "BlockType": "PAGE",
                    "Text": "This is some content, it should not be included",
                },
                {
                    "BlockType": "WORD",
                    "Text": "This is a word, it should not be included",
                },
                {
                    "BlockType": "LINE",
                    "Text": "This is line 1",
                },
                {
                    "BlockType": "LINE",
                    "Text": "This is line 2",
                },
            ],
        }
    return orig(self, operation_name, kwarg)


def mock_make_api_call_failure(self, operation_name, kwarg):
    if operation_name == "DetectDocumentText":
        raise Exception("The Textract client failed!")
    return orig(self, operation_name, kwarg)


# Mocked botocore _make_api_call function
def mock_make_api_call_bad_response(self, operation_name, kwarg):
    if operation_name == 'DetectDocumentText':
        return {"badkey": ["array", "array"]}
    return orig(self, operation_name, kwarg)


class TestPdfExtractor(unittest.TestCase):
    CONFIG = {
        "textract": {
            "aws_access_key_id": "xxxxxx",
            "aws_secret_access_key": "xxxxxx",
            "aws_region": "us-east-1",
        },
    }

    def _load_pdf(self):
        # load pdf file
        with open("extractors/tests/fixtures/sample.pdf", "rb") as f:
            file = f.read()
        return file

    def test_create(self):
        extractor = Extractor.get_extractor("application/pdf", self.CONFIG)
        self.assertIsInstance(extractor, PdfExtractor)

    # This test is all-encompassing. It tests if image conversion, response parsing, and multipage support is working.
    def test_extract(self):
        extractor = Extractor.get_extractor("application/pdf", self.CONFIG)
        file = self._load_pdf()
        # patch textract call and run extractor
        with patch('botocore.client.BaseClient._make_api_call', new=mock_make_api_call):
            output = extractor.extract(file)
            # since we can't test PDF extraction directly, we can instead ensure that multipage support is working by
            # counting the number of "This is line 1 This is line 2 "'s we have in our output. There should be one per page.
            # since the sample PDF has two pages, multiply the expected string by two.
            self.assertEqual(output, "This is line 1 This is line 2 " * 2)

    # Tests if the Textract client exception is caught
    def test_extract_failure(self):
        extractor = Extractor.get_extractor("application/pdf", self.CONFIG)
        file = self._load_pdf()
        with patch('botocore.client.BaseClient._make_api_call', new=mock_make_api_call_failure):
            with self.assertRaises(ExtractorException):
                extractor.extract(file)

    # Tests if sending a bad PDF is caught
    def test_bad_file(self):
        extractor = Extractor.get_extractor("application/pdf", self.CONFIG)
        file = b"This is valid bytes but not a valid PDF"
        with patch('botocore.client.BaseClient._make_api_call', new=mock_make_api_call):
            with self.assertRaises(ExtractorException):
                extractor.extract(file)

    # Test if improper AWS response is caught
    def test_bad_response(self):
        extractor = Extractor.get_extractor("application/pdf", self.CONFIG)
        file = self._load_pdf()
        with patch('botocore.client.BaseClient._make_api_call', new=mock_make_api_call_bad_response):
            with self.assertRaises(ExtractorException):
                extractor.extract(file)
