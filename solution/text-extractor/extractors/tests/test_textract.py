from unittest.mock import patch

import botocore
from magika import Magika

from extractors import (
    Extractor,
    ExtractorException,
)

from . import FixtureTestCase

# Original botocore _make_api_call function
orig = botocore.client.BaseClient._make_api_call


# Mocked botocore _make_api_call function
def mock_make_api_call(self, operation_name, kwarg):
    accepted_types = [
        "image/jpeg",
        "image/tiff",
        "image/png",
    ]

    if operation_name == 'DetectDocumentText':
        doc = kwarg["Document"]["Bytes"]
        file_type = Magika().identify_bytes(doc).output.mime_type
        if file_type not in accepted_types:
            raise Exception("Received an invalid type!")
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


# Mocked botocore _make_api_call function that fails every time
def mock_make_api_call_failure(self, operation_name, kwarg):
    if operation_name == "DetectDocumentText":
        raise Exception("The Textract client failed!")
    return orig(self, operation_name, kwarg)


# Mocked botocore _make_api_call function that returns an invalid response
def mock_make_api_call_bad_response(self, operation_name, kwarg):
    if operation_name == 'DetectDocumentText':
        return {"badkey": ["array", "array"]}
    return orig(self, operation_name, kwarg)


class TestTextractExtractor(FixtureTestCase):
    CONFIG = {
        "aws": {
            "aws_access_key_id": "xxxxxx",
            "aws_secret_access_key": "xxxxxx",
            "aws_region": "us-east-1",
        },
    }

    @patch.object(botocore.client.BaseClient, "_make_api_call", mock_make_api_call)
    def test_extract_jpg(self):
        self._test_file_type("jpg", collection="textract", config=self.CONFIG)

    @patch.object(botocore.client.BaseClient, "_make_api_call", mock_make_api_call)
    def test_extract_jpeg(self):
        self._test_file_type("jpeg", collection="textract", config=self.CONFIG)

    @patch.object(botocore.client.BaseClient, "_make_api_call", mock_make_api_call)
    def test_extract_png(self):
        self._test_file_type("png", collection="textract", config=self.CONFIG)

    @patch.object(botocore.client.BaseClient, "_make_api_call", mock_make_api_call)
    def test_extract_tiff(self):
        self._test_file_type("tiff", collection="textract", config=self.CONFIG)

    @patch.object(botocore.client.BaseClient, "_make_api_call", mock_make_api_call_failure)
    def test_extract_failure(self):
        with self.assertRaises(ExtractorException):
            self._test_file_type("jpg", collection="textract", config=self.CONFIG)

    @patch.object(botocore.client.BaseClient, "_make_api_call", mock_make_api_call)
    def test_bad_file(self):
        extractor = Extractor.get_extractor("image/jpeg", self.CONFIG)
        data = b"This is a valid string but not a valid type for Textract"
        with self.assertRaises(ExtractorException):
            extractor.extract(data)

    @patch.object(botocore.client.BaseClient, "_make_api_call", mock_make_api_call_bad_response)
    def test_bad_response(self):
        with self.assertRaises(ExtractorException):
            self._test_file_type("jpg", collection="textract", config=self.CONFIG)
