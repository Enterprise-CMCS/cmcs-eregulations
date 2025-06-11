import json
import os
from unittest.mock import patch

from . import FixtureTestCase, mock_extract_embedded
from extractors import Extractor


class TestZipExtractor(FixtureTestCase):
    def test_extract(self):
        sample_path = os.path.join(self.BASE_PATH, "zip", "sample.zip")
        with open(sample_path, "rb") as f:
            sample = f.read()

        expected_path = os.path.join(self.BASE_PATH, "zip", "expected.json")
        with open(expected_path, "r") as f:
            expected = json.load(f)

        with patch("extractors.Extractor._extract_embedded", new=mock_extract_embedded):
            extractor = Extractor.get_extractor("zip")
            output = extractor.extract(sample)

        for string in expected:
            self.assertIn(string, output, f"Expected string '{string}' not found in output.")

        self.assertEqual(len(output.strip()), len(" ".join(expected).strip()))
