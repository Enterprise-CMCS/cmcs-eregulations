import json
import os
import sys
import types
import unittest
from importlib import util
from pathlib import Path
from unittest.mock import patch

from common.auth import BackendCredentials


def _load_module():
    worker_dir = Path(__file__).resolve().parent.parent / "ecfr-worker"
    module_path = worker_dir / "app.py"

    package_name = "ecfr_worker_pkg"
    package = types.ModuleType(package_name)
    package.__path__ = [str(worker_dir)]
    sys.modules[package_name] = package

    spec = util.spec_from_file_location(f"{package_name}.app", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load ecfr worker app module")
    module = util.module_from_spec(spec)
    sys.modules[f"{package_name}.app"] = module
    spec.loader.exec_module(module)
    return module


_module = _load_module()
config_spec = util.spec_from_file_location(
    "ecfr_worker_pkg.config",
    Path(__file__).resolve().parent.parent / "ecfr-worker" / "config.py",
)
if config_spec is None or config_spec.loader is None:
    raise RuntimeError("Unable to load ecfr worker config module")
_config_module = util.module_from_spec(config_spec)
sys.modules["ecfr_worker_pkg.config"] = _config_module
config_spec.loader.exec_module(_config_module)


class EcfrWorkerAppTests(unittest.TestCase):
    def _build_parsed_config(self, *, upload_reg_text: bool, upload_locations: bool):
        return _config_module.parse_config(
            {
                "config": {
                    "title_number": 42,
                    "part_number": 400,
                    "effective_date": "2025-01-01",
                    "upload_reg_text": upload_reg_text,
                    "upload_locations": upload_locations,
                    "credentials": {
                        "auth_type": "basic",
                        "username": "u",
                        "password": "p",
                    },
                }
            }
        )

    def test_handler_uploads_part_with_flags_enabled(self):
        parsed_config = self._build_parsed_config(upload_reg_text=True, upload_locations=True)

        structure = {
            "type": "title",
            "identifier": "42",
            "children": [],
        }

        with patch.dict(os.environ, {"EREGS_API_URL_V3": "https://example.local/v3/"}, clear=True), patch.object(
            _module, "parse_config_from_event", return_value=parsed_config
        ), patch.object(_module, "fetch_part_structure", return_value=structure), patch.object(
            _module, "determine_part_depth", return_value=3
        ), patch.object(
            _module, "fetch_part_full_xml", return_value="<xml/>"
        ), patch.object(
            _module,
            "extract_sections_and_subparts",
            return_value=(
                [{"title": "42", "part": "400", "section": "200"}],
                [{"title": "42", "part": "400", "subpart": "B", "sections": []}],
            ),
        ), patch.object(
            _module,
            "upload_part",
            return_value={"ok": True},
        ) as mock_upload:
            response = _module.handler({"body": "{}"}, None)

        body = json.loads(response["body"])
        self.assertEqual(body["processed"], 1)
        self.assertTrue(body["uploaded"])

        upload_payload = mock_upload.call_args.kwargs["payload"]
        self.assertEqual(upload_payload["name"], "400")
        self.assertEqual(upload_payload["title"], "42")
        self.assertEqual(upload_payload["date"], "2025-01-01")
        self.assertEqual(upload_payload["document"], {"raw_xml": "<xml/>"})
        self.assertEqual(upload_payload["depth"], 3)
        self.assertEqual(len(upload_payload["sections"]), 1)
        self.assertEqual(len(upload_payload["subparts"]), 1)

    def test_handler_skips_full_xml_and_locations_when_flags_disabled(self):
        parsed_config = self._build_parsed_config(upload_reg_text=False, upload_locations=False)

        structure = {
            "type": "title",
            "identifier": "42",
            "children": [],
        }

        with patch.dict(os.environ, {"EREGS_API_URL_V3": "https://example.local/v3/"}, clear=True), patch.object(
            _module, "parse_config_from_event", return_value=parsed_config
        ), patch.object(_module, "fetch_part_structure", return_value=structure), patch.object(
            _module, "determine_part_depth", return_value=3
        ), patch.object(
            _module,
            "upload_part",
            return_value={"ok": True},
        ) as mock_upload, patch.object(_module, "fetch_part_full_xml") as mock_fetch_xml, patch.object(
            _module, "extract_sections_and_subparts"
        ) as mock_extract:
            response = _module.handler({"body": "{}"}, None)

        body = json.loads(response["body"])
        self.assertEqual(body["processed"], 1)

        upload_payload = mock_upload.call_args.kwargs["payload"]
        self.assertEqual(upload_payload["document"], {})
        self.assertEqual(upload_payload["sections"], [])
        self.assertEqual(upload_payload["subparts"], [])

        mock_fetch_xml.assert_not_called()
        mock_extract.assert_not_called()


if __name__ == "__main__":
    unittest.main()
