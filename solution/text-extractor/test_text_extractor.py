import unittest
import json

from text_extractor import clean_output, get_config


class TextExtractorTestCase(unittest.TestCase):
    def test_clean_output(self):
        text = "Hello   \n  \n\n world \0 \t\r \x00"
        expected = "Hello world"
        output = clean_output(text)
        self.assertEqual(output, expected)

    def test_clean_output_all_unicode(self):
        text = "".join(chr(ch) for ch in range(0x0000, 0x0020))  # String containing all control characters
        output = clean_output(text)
        self.assertEqual(output, "")

    def test_get_config_normal_invocation(self):
        body = {
            "hello": "world",
            "x": 1,
        }

        event = {
            "body": json.dumps(body),
            "something": "else",
        }

        output = get_config(event)
        self.assertEqual(output, body)

    def test_get_config_json_failure(self):
        event = {
            "body": "{this: is, invalid: json,\}",
            "something": "else",
        }

        with self.assertRaises(Exception):
            get_config(event)

    def test_get_config_direct_invocation(self):
        event = {
            "param1": "value1",
            "param2": 0,
        }

        output = get_config(event)
        self.assertEqual(output, event)
