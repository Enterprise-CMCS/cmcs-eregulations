import unittest
from unittest.mock import patch

import botocore
import magic

from . import FileComparisonMixin

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


class TestEmailExtractor(unittest.TestCase, FileComparisonMixin):
    CONFIG = {
        "aws": {
            "aws_access_key_id": "xxxxxx",
            "aws_secret_access_key": "xxxxxx",
            "aws_region": "us-east-1",
        },
    }

    def test_extract(self):
        with patch('botocore.client.BaseClient._make_api_call', new=mock_make_api_call):
            self._test_file_type("eml", config=self.CONFIG)

    def test_extract_failure(self):
        with patch('botocore.client.BaseClient._make_api_call', new=mock_make_api_call_failure):
            self._test_file_type("eml", variation="pdf")
