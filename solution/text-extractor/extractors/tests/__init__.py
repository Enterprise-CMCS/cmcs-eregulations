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

        with open(f"{self.BASE_PATH}{file_type}/{variation}sample.{file_type}", "rb") as f:
            sample = f.read()
        with open(f"{self.BASE_PATH}{file_type}/{variation}expected.txt", "rb") as f:
            expected = f.read().decode()

        with patch("extractors.Extractor._extract_embedded", new=mock_extract_embedded):
            extractor = Extractor.get_extractor(file_type, config)
            output = extractor.extract(sample)

        # Uncomment these 2 lines to re-export fixture files the next time tests are run.
        # with open(f"{self.BASE_PATH}{file_type}/{variation}expected.txt", "w") as f:
        #     f.write(output)

        self.assertEqual(output, expected)
