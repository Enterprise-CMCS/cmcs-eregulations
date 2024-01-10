import json
import logging
import unittest

from utils import (
    clean_output,
    get_config,
    lambda_failure,
    lambda_response,
    lambda_success,
)

logging.disable(logging.CRITICAL)


class UtilsTestCase(unittest.TestCase):
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
            "body": "{this: is, invalid: json,}",
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

    def test_lambda_response(self):
        output = lambda_response(100, logging.ERROR, "Hello world")
        self.assertEqual(output, {
            "statusCode": 100,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Hello world"}),
        })

    def test_lambda_success(self):
        output = lambda_success("Hello world")
        self.assertEqual(output["statusCode"], 200)

    def test_lambda_failure(self):
        output = lambda_failure(400, "Hello world")
        self.assertEqual(output["statusCode"], 400)
