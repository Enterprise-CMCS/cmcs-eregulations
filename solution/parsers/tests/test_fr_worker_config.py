import unittest
from importlib import util
from pathlib import Path
from unittest.mock import patch

from common.config import ConfigParseError

from common.auth import BackendCredentials


def _load_module():
    module_path = Path(__file__).resolve().parent.parent / "fr-worker" / "config.py"
    spec = util.spec_from_file_location("fr_worker_config", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load fr worker config module")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_module = _load_module()
parse_config = _module.parse_config


def _payload(**overrides):
    payload = {
        "config": {
            "document_number": "2026-12345",
            "title": 42,
            "part": "400",
            "description": "A document title",
            "name": "90 FR 1",
            "doc_type": "Rule",
            "url": "https://example/x",
            "date": "2026-01-01",
            "docket_numbers": ["ABC-1", "DEF-2"],
            "raw_text_url": "https://example/x.txt",
            "full_text_xml_url": "https://example/x.xml",
            "log_level": "warn",
        }
    }
    payload["config"].update(overrides)
    return payload


class FrWorkerConfigTests(unittest.TestCase):
    def test_parse_config_full_document(self):
        with patch.dict("os.environ", {"EREGS_USERNAME": "env-user", "EREGS_PASSWORD": "env-pass"}, clear=True):
            parsed = parse_config(_payload())

        self.assertEqual(parsed.document_number, "2026-12345")
        self.assertEqual(parsed.title, 42)
        self.assertEqual(parsed.part, "400")
        self.assertEqual(parsed.description, "A document title")
        self.assertEqual(parsed.name, "90 FR 1")
        self.assertEqual(parsed.doc_type, "Rule")
        self.assertEqual(parsed.url, "https://example/x")
        self.assertEqual(parsed.date, "2026-01-01")
        self.assertEqual(parsed.docket_numbers, ["ABC-1", "DEF-2"])
        self.assertEqual(parsed.raw_text_url, "https://example/x.txt")
        self.assertEqual(parsed.full_text_xml_url, "https://example/x.xml")
        self.assertEqual(parsed.log_level, "WARNING")
        self.assertEqual(parsed.credentials, BackendCredentials("basic", "env-user", "env-pass", None))

    def test_parse_config_rejects_invalid_log_level(self):
        with patch.dict("os.environ", {"EREGS_USERNAME": "env-user", "EREGS_PASSWORD": "env-pass"}, clear=True):
            with self.assertRaisesRegex(ConfigParseError, "loglevel must be one of"):
                parse_config(_payload(log_level="verbose"))

    def test_parse_config_rejects_missing_title(self):
        payload = _payload()
        del payload["config"]["title"]
        with patch.dict("os.environ", {"EREGS_USERNAME": "u", "EREGS_PASSWORD": "p"}, clear=True):
            with self.assertRaises(ConfigParseError):
                parse_config(payload)

    def test_parse_config_rejects_non_list_docket_numbers(self):
        with patch.dict("os.environ", {"EREGS_USERNAME": "u", "EREGS_PASSWORD": "p"}, clear=True):
            with self.assertRaisesRegex(ConfigParseError, "docket_numbers must be a list"):
                parse_config(_payload(docket_numbers="ABC-1"))

    def test_parse_config_allows_missing_full_text_xml_url(self):
        payload = _payload()
        del payload["config"]["full_text_xml_url"]
        with patch.dict("os.environ", {"EREGS_USERNAME": "u", "EREGS_PASSWORD": "p"}, clear=True):
            parsed = parse_config(payload)

        self.assertIsNone(parsed.full_text_xml_url)

    def test_parse_config_treats_blank_full_text_xml_url_as_none(self):
        with patch.dict("os.environ", {"EREGS_USERNAME": "u", "EREGS_PASSWORD": "p"}, clear=True):
            parsed = parse_config(_payload(full_text_xml_url="   "))

        self.assertIsNone(parsed.full_text_xml_url)

    def test_parse_config_rejects_non_string_full_text_xml_url(self):
        with patch.dict("os.environ", {"EREGS_USERNAME": "u", "EREGS_PASSWORD": "p"}, clear=True):
            with self.assertRaisesRegex(ConfigParseError, "full_text_xml_url must be a string"):
                parse_config(_payload(full_text_xml_url=123))

    def test_parse_config_rejects_missing_required_field(self):
        with patch.dict("os.environ", {"EREGS_USERNAME": "u", "EREGS_PASSWORD": "p"}, clear=True):
            with self.assertRaises(ConfigParseError):
                parse_config(_payload(raw_text_url=""))


if __name__ == "__main__":
    unittest.main()
