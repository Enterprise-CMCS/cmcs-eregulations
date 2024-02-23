import logging
import unittest
from unittest.mock import patch

from extractors import Extractor

import magic
import filetype


logging.disable(logging.CRITICAL)


def mock_extract_embedded(self, file_name: str, file: bytes) -> str:
    return f"Embedded file {file_name}"


class FixtureTestCase(unittest.TestCase):
    BASE_PATH = "extractors/tests/fixtures/"
    
    def _test_file_type(self, file_type, **kwargs):
        variation = kwargs.get("variation", None)
        variation = f"{variation}_" if variation else ""
        config = kwargs.get("config", {})
        collection = kwargs.get("collection", file_type)  # Use 'collection' if expected.txt is the same for multiple types

        with open(f"{self.BASE_PATH}{collection}/{variation}sample.{file_type}", "rb") as f:
            sample = f.read()
        with open(f"{self.BASE_PATH}{collection}/{variation}expected.txt", "rb") as f:
            expected = f.read().decode()

        # Determine the file's MIME type
        try:
            mime_type = filetype.guess_mime(sample)
            if not mime_type or mime_type == "application/octet-stream":
                raise Exception
        except Exception:
            mime_type = magic.from_buffer(sample, mime=True)

        with patch("extractors.Extractor._extract_embedded", new=mock_extract_embedded):
            extractor = Extractor.get_extractor(mime_type, config)
            output = extractor.extract(sample)

        # Uncomment these 2 lines to re-export fixture files the next time tests are run.
        # with open(f"{self.BASE_PATH}{collection}/{variation}expected.txt", "w") as f:
        #     f.write(output)

        self.assertEqual(output, expected)
