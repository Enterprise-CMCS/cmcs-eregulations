import unittest

from common.config import (
    ConfigParseError,
    parse_credentials,
    parse_message_body,
    require_non_empty_string,
    require_positive_int,
    require_single_record,
    unwrap_config,
)


class CommonConfigTests(unittest.TestCase):
    def test_parse_message_body_returns_dict(self):
        record = {"body": '{"config": {"title_number": 42}}'}
        payload = parse_message_body(record)
        self.assertEqual(payload, {"config": {"title_number": 42}})

    def test_parse_message_body_rejects_missing_body(self):
        with self.assertRaisesRegex(ConfigParseError, "non-empty JSON string"):
            parse_message_body({})

    def test_parse_message_body_rejects_invalid_json(self):
        with self.assertRaisesRegex(ConfigParseError, "valid JSON"):
            parse_message_body({"body": "{invalid"})

    def test_parse_message_body_rejects_non_object_json(self):
        with self.assertRaisesRegex(ConfigParseError, "JSON object"):
            parse_message_body({"body": '["not", "an", "object"]'})

    def test_unwrap_config_supports_wrapped_and_direct_payloads(self):
        wrapped = unwrap_config({"config": {"part_number": 400}})
        direct = unwrap_config({"part_number": 400})
        self.assertEqual(wrapped, {"part_number": 400})
        self.assertEqual(direct, {"part_number": 400})

    def test_unwrap_config_rejects_non_object(self):
        with self.assertRaisesRegex(ConfigParseError, "config must be a JSON object"):
            unwrap_config({"config": "bad"})

    def test_require_single_record(self):
        record = {"body": "{}"}
        self.assertEqual(require_single_record([record]), record)

        with self.assertRaisesRegex(ConfigParseError, "Expected exactly 1 SQS record"):
            require_single_record([])

        with self.assertRaisesRegex(ConfigParseError, "SQS record must be a JSON object"):
            require_single_record(["bad"])

    def test_parse_credentials_basic_and_default_auth_type(self):
        creds = parse_credentials({"username": "user", "password": "pass"})
        self.assertEqual(creds.auth_type, "basic")
        self.assertEqual(creds.username, "user")
        self.assertEqual(creds.password, "pass")

    def test_parse_credentials_bearer(self):
        creds = parse_credentials({"auth_type": "bearer", "token": "abc"})
        self.assertEqual(creds.auth_type, "bearer")
        self.assertEqual(creds.token, "abc")

    def test_parse_credentials_rejects_invalid(self):
        with self.assertRaisesRegex(ConfigParseError, "credentials must be a JSON object"):
            parse_credentials("bad")

        with self.assertRaisesRegex(ConfigParseError, "must be 'basic' or 'bearer'"):
            parse_credentials({"auth_type": "oauth"})

    def test_require_positive_int(self):
        self.assertEqual(require_positive_int({"title_number": 42}, "title_number"), 42)
        with self.assertRaisesRegex(ConfigParseError, "positive integer"):
            require_positive_int({"title_number": 0}, "title_number")

    def test_require_non_empty_string(self):
        self.assertEqual(require_non_empty_string({"document_number": " 2026-123 "}, "document_number"), "2026-123")
        with self.assertRaisesRegex(ConfigParseError, "non-empty string"):
            require_non_empty_string({"document_number": "   "}, "document_number")


if __name__ == "__main__":
    unittest.main()
