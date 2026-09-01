import unittest

from common.ecfr import (
    ECFR_V1_BASE_URL,
    extract_part_numbers,
    identifier_to_part_number,
    parse_part_number,
    parse_subchapter_value,
)
from common.eregs_config import EregsConfigError


class CommonEcfrTests(unittest.TestCase):
    def test_base_url_default(self):
        self.assertEqual(ECFR_V1_BASE_URL, "https://www.ecfr.gov/api/versioner/v1/")

    def test_extract_part_numbers_collects_unique_sorted(self):
        payload = {
            "type": "chapter",
            "children": [
                {"type": "subchapter", "children": [
                    {"type": "part", "identifier": "400"},
                    {"type": "part", "identifier": ["401"]},
                    {"type": "part", "identifier": "400"},
                    {"type": "nested", "children": [
                        {"type": "part", "identifier": "401"},
                    ]},
                ]},
            ],
        }
        self.assertEqual(extract_part_numbers(payload), [400, 401])

    def test_extract_part_numbers_ignores_non_numeric(self):
        payload = {
            "type": "part",
            "identifier": "C1",
            "children": [
                {"type": "part", "identifier": "400"},
            ],
        }
        self.assertEqual(extract_part_numbers(payload), [400])

    def test_identifier_to_part_number(self):
        self.assertEqual(identifier_to_part_number("400"), 400)
        self.assertEqual(identifier_to_part_number(["401"]), 401)
        self.assertIsNone(identifier_to_part_number("ABC"))
        self.assertIsNone(identifier_to_part_number([]))
        self.assertIsNone(identifier_to_part_number(None))

    def test_parse_part_number_valid(self):
        self.assertEqual(parse_part_number("400"), 400)

    def test_parse_part_number_invalid(self):
        with self.assertRaises(EregsConfigError):
            parse_part_number("ABC")

    def test_parse_subchapter_value_valid(self):
        self.assertEqual(parse_subchapter_value("IV-C"), ("IV", "C"))

    def test_parse_subchapter_value_invalid(self):
        with self.assertRaises(EregsConfigError):
            parse_subchapter_value("IV")


if __name__ == "__main__":
    unittest.main()
