import logging
import unittest
from unittest.mock import patch

from extractors import Extractor


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

        # Determine the file's content type
        file_type = Extractor.get_file_type(sample)

        with patch("extractors.Extractor._extract_embedded", new=mock_extract_embedded):
            extractor = Extractor.get_extractor(file_type, config)
            output = extractor.extract(sample)

        # Uncomment these 2 lines to re-export fixture files the next time tests are run.
        with open(f"{self.BASE_PATH}{collection}/{variation}expected.txt", "w") as f:
            f.write(output)

        with open(f"{self.BASE_PATH}{collection}/{variation}expected.txt", "rb") as f:
            expected = f.read().decode()

        self.assertEqual(output, expected)
