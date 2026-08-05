import unittest
from importlib import util
from pathlib import Path

from common.auth import BackendCredentials
from common.config import ConfigParseError


def _load_module():
    module_path = Path(__file__).resolve().parent.parent / "ecfr-worker" / "config.py"
    spec = util.spec_from_file_location("ecfr_worker_config", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load ecfr worker config module")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_module = _load_module()
parse_config = _module.parse_config


class EcfrWorkerConfigTests(unittest.TestCase):
    def test_parse_config_requires_effective_date_and_flags(self):
        payload = {
            "config": {
                "title_number": 42,
                "part_number": 400,
                "effective_date": "2025-01-01",
                "upload_reg_text": True,
                "upload_locations": False,
                "credentials": {
                    "auth_type": "basic",
                    "username": "queue-user",
                    "password": "queue-pass",
                },
            }
        }

        parsed = parse_config(payload)

        self.assertEqual(parsed.title_number, 42)
        self.assertEqual(parsed.part_number, 400)
        self.assertEqual(parsed.effective_date, "2025-01-01")
        self.assertTrue(parsed.upload_reg_text)
        self.assertFalse(parsed.upload_locations)
        self.assertEqual(parsed.credentials, BackendCredentials("basic", "queue-user", "queue-pass", None))

    def test_parse_config_rejects_missing_effective_date(self):
        payload = {
            "config": {
                "title_number": 42,
                "part_number": 400,
                "upload_reg_text": True,
                "upload_locations": True,
                "credentials": {
                    "auth_type": "basic",
                    "username": "queue-user",
                    "password": "queue-pass",
                },
            }
        }

        with self.assertRaisesRegex(ConfigParseError, "effective_date must be a non-empty string"):
            parse_config(payload)

    def test_parse_config_rejects_non_boolean_flags(self):
        payload = {
            "config": {
                "title_number": 42,
                "part_number": 400,
                "effective_date": "2025-01-01",
                "upload_reg_text": "yes",
                "upload_locations": True,
                "credentials": {
                    "auth_type": "basic",
                    "username": "queue-user",
                    "password": "queue-pass",
                },
            }
        }

        with self.assertRaisesRegex(ConfigParseError, "upload_reg_text must be a boolean"):
            parse_config(payload)


if __name__ == "__main__":
    unittest.main()
