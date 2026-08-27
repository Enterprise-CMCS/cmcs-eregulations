import unittest
from unittest.mock import patch
from importlib import util
from pathlib import Path

from common.auth import BackendCredentials
from common.config import ConfigParseError


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


class FrWorkerConfigTests(unittest.TestCase):
    def test_parse_config_requires_document_number_and_log_level(self):
        payload = {
            "config": {
                "document_number": "2026-12345",
                "log_level": "warn",
            }
        }

        with patch.dict("os.environ", {"EREGS_USERNAME": "env-user", "EREGS_PASSWORD": "env-pass"}, clear=True):
            parsed = parse_config(payload)

        self.assertEqual(parsed.document_number, "2026-12345")
        self.assertEqual(parsed.log_level, "WARNING")
        self.assertEqual(parsed.credentials, BackendCredentials("basic", "env-user", "env-pass", None))

    def test_parse_config_rejects_invalid_log_level(self):
        payload = {
            "config": {
                "document_number": "2026-12345",
                "log_level": "verbose",
            }
        }

        with patch.dict("os.environ", {"EREGS_USERNAME": "env-user", "EREGS_PASSWORD": "env-pass"}, clear=True):
            with self.assertRaisesRegex(ConfigParseError, "loglevel must be one of"):
                parse_config(payload)


if __name__ == "__main__":
    unittest.main()
