import base64
import unittest
from importlib import util
from pathlib import Path
from unittest.mock import Mock, patch

from common.auth import BackendCredentials


def _load_module():
    module_path = Path(__file__).resolve().parent.parent / "ecfr-launcher" / "eregs_config.py"
    spec = util.spec_from_file_location("ecfr_launcher_config", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load eregs_config module")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_module = _load_module()
EregsConfigError = _module.EregsConfigError
TargetPartConfig = _module.TargetPartConfig
expand_target_parts = _module.expand_target_parts
fetch_parser_config = _module.fetch_parser_config
fetch_existing_part_dates_by_title = _module.fetch_existing_part_dates_by_title
fetch_subchapter_part_numbers = _module.fetch_subchapter_part_numbers


class EcfrLauncherConfigTests(unittest.TestCase):
    def test_fetch_parser_config_uses_basic_auth(self):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"parts": []}

        with patch("requests.get", return_value=response) as mock_get:
            payload = fetch_parser_config(
                api_base_url="https://example.local/v3/",
                credentials=BackendCredentials(auth_type="basic", username="user", password="pass"),
            )

        self.assertEqual(payload, {"parts": []})
        expected_auth = "Basic " + base64.b64encode(b"user:pass").decode("utf-8")
        self.assertEqual(mock_get.call_args.kwargs["headers"]["Authorization"], expected_auth)

    def test_fetch_existing_part_dates_by_title_uses_basic_auth(self):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = [
            {"name": "400", "date": "2025-01-01"},
            {"name": "abc", "date": "2025-01-01"},
            {"name": "401", "date": ""},
        ]

        with patch("requests.get", return_value=response) as mock_get:
            payload = fetch_existing_part_dates_by_title(
                api_base_url="https://example.local/v3/",
                credentials=BackendCredentials(auth_type="basic", username="user", password="pass"),
                title_number=42,
            )

        self.assertEqual(payload, {400: "2025-01-01"})
        expected_auth = "Basic " + base64.b64encode(b"user:pass").decode("utf-8")
        self.assertEqual(mock_get.call_args.kwargs["headers"]["Authorization"], expected_auth)

    def test_expand_target_parts_part_passthrough(self):
        parser_config = {
            "parts": [
                {
                    "title": 42,
                    "type": "part",
                    "value": "400",
                    "upload_reg_text": True,
                    "upload_locations": False,
                }
            ]
        }

        targets = expand_target_parts(parser_config)

        self.assertEqual(
            targets,
            [
                TargetPartConfig(
                    title_number=42,
                    part_number=400,
                    upload_reg_text=True,
                    upload_locations=False,
                )
            ],
        )

    @patch.object(_module, "fetch_subchapter_part_numbers", return_value=[400, 401])
    def test_expand_target_parts_subchapter_expansion(self, mock_fetch):
        parser_config = {
            "parts": [
                {
                    "title": 42,
                    "type": "subchapter",
                    "value": "IV-C",
                    "upload_reg_text": True,
                    "upload_locations": True,
                }
            ]
        }

        targets = expand_target_parts(parser_config)

        self.assertEqual(
            targets,
            [
                TargetPartConfig(42, 400, True, True),
                TargetPartConfig(42, 401, True, True),
            ],
        )
        mock_fetch.assert_called_once_with(
            title_number=42,
            chapter="IV",
            subchapter="C",
            timeout=60,
            base_url=_module.ECFR_V1_BASE_URL,
        )

    def test_expand_target_parts_invalid_subchapter_value(self):
        parser_config = {
            "parts": [
                {
                    "title": 42,
                    "type": "subchapter",
                    "value": "invalid",
                    "upload_reg_text": True,
                    "upload_locations": True,
                }
            ]
        }

        with self.assertRaisesRegex(EregsConfigError, "CHAPTER-SUBCHAPTER"):
            expand_target_parts(parser_config)

    def test_expand_target_parts_invalid_title_type(self):
        parser_config = {
            "parts": [
                {
                    "title": "42",
                    "type": "part",
                    "value": "400",
                    "upload_reg_text": True,
                    "upload_locations": True,
                }
            ]
        }

        with self.assertRaisesRegex(EregsConfigError, r"title must be a positive integer"):
            expand_target_parts(parser_config)

    @patch("requests.get")
    def test_fetch_subchapter_part_numbers(self, mock_get):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "type": "title",
            "children": [
                {
                    "type": "chapter",
                    "children": [
                        {
                            "type": "subchapter",
                            "children": [
                                {"type": "part", "identifier": "400"},
                                {"type": "part", "identifier": "401"},
                            ],
                        }
                    ],
                }
            ],
        }
        mock_get.return_value = response

        part_numbers = fetch_subchapter_part_numbers(
            title_number=42,
            chapter="IV",
            subchapter="C",
        )

        self.assertEqual(part_numbers, [400, 401])


if __name__ == "__main__":
    unittest.main()
