import os
import json
import logging
import unittest
import base64

from utils import (
    clean_output,
    get_config,
    lambda_response,
    configure_authorization,
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

    def test_get_config_sqs_invocation(self):
        record = {
            "hello": "world",
            "x": 1,
            "sqs_group": "some-group",
        }

        body = {
            "not": "what we want",
        }

        event = {
            "Records": [
                {
                    "body": json.dumps(record),
                    "attributes": {
                        "MessageGroupId": "some-group",
                    },
                },
                {
                    "body": json.dumps(body),
                    "attributes": {
                        "MessageGroupId": "some-other-group",
                    },
                },
            ],
            "body": json.dumps(body),
        }

        output = get_config(event)
        self.assertEqual(output, record)

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
        output = lambda_response(100, "Hello world")
        self.assertEqual(output, {
            "statusCode": 100,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Hello world"}),
        })

    def test_config_auth_basic(self):
        auth = {
            "type": "basic",
            "username": "abc",
            "password": "123",
        }

        username = auth["username"]
        password = auth["password"]
        creds = f"{username}:{password}"
        token = base64.b64encode(creds.encode("utf-8")).decode("utf-8")
        authorization = f"Basic {token}"

        self.assertEqual(configure_authorization(auth), authorization)

    def test_config_auth_basic_env(self):
        auth = {
            "type": "basic-env",
            "username": "USERNAME",
            "password": "PASSWORD",
        }

        username = "a-username"
        password = "a-password"
        os.environ["USERNAME"] = username
        os.environ["PASSWORD"] = password

        creds = f"{username}:{password}"
        token = base64.b64encode(creds.encode("utf-8")).decode("utf-8")
        authorization = f"Basic {token}"

        self.assertEqual(configure_authorization(auth), authorization)

    def test_config_auth_token(self):
        auth = {
            "type": "token",
            "token": "some-token",
        }
        authorization = f"Bearer {auth['token']}"
        self.assertEqual(configure_authorization(auth), authorization)

    def test_config_auth_bad_type(self):
        auth = {
            "type": "unknown",
            "token": "some-token",
        }
        with self.assertRaises(Exception):
            configure_authorization(auth)

    ### TODO: test AWS secrets manager here
