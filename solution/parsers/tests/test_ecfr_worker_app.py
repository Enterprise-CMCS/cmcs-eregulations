import json
import os
import sys
import types
import unittest
from importlib import util
from pathlib import Path
from types import SimpleNamespace
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


class EcfrWorkerAppTests(unittest.TestCase):
    def _build_parsed_config(self, *, upload_reg_text: bool, upload_locations: bool):
        return SimpleNamespace(
            parser_result_id=7,
            title_number=42,
            part_number=400,
            effective_date="2025-01-01",
            upload_reg_text=upload_reg_text,
            upload_locations=upload_locations,
            log_level="INFO",
            credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
        )

    def test_handler_updates_result_to_succeeded(self):
        parsed_config = self._build_parsed_config(upload_reg_text=True, upload_locations=True)

        structure = {"type": "title", "identifier": "42", "children": []}

        with patch.dict(os.environ, {"EREGS_API_URL_V3": "https://example.local/v3/"}, clear=True), patch.object(
            _module, "parse_config_from_event", return_value=parsed_config
        ), patch.object(_module, "fetch_part_structure", return_value=structure), patch.object(
            _module, "determine_part_depth", return_value=3
        ), patch.object(
            _module, "fetch_part_full_xml", return_value="<xml/>"
        ), patch.object(
            _module,
            "parse_part_xml_to_document",
            return_value={"node_type": "part", "children": []},
        ), patch.object(
            _module,
            "extract_sections_and_subparts",
            return_value=(
                [{"title": "42", "part": "400", "section": "200"}],
                [{"title": "42", "part": "400", "subpart": "B", "sections": []}],
            ),
        ), patch.object(_module, "upload_part", return_value={"id": 123, "status": "ok"}), patch.object(
            _module, "update_ecfr_result", return_value={"id": 7, "status": "succeeded"}
        ) as mock_update_result:
            response = _module.handler({"body": "{}"}, None)

        body = json.loads(response["body"])
        self.assertEqual(body["processed"], 1)
        self.assertTrue(body["uploaded"])
        self.assertEqual(mock_update_result.call_args.kwargs["result_id"], 7)
        self.assertEqual(mock_update_result.call_args.kwargs["payload"]["status"], "succeeded")

    def test_handler_updates_result_to_failed_and_reraises(self):
        parsed_config = self._build_parsed_config(upload_reg_text=True, upload_locations=True)

        with patch.dict(os.environ, {"EREGS_API_URL_V3": "https://example.local/v3/"}, clear=True), patch.object(
            _module, "parse_config_from_event", return_value=parsed_config
        ), patch.object(
            _module, "fetch_part_structure", side_effect=RuntimeError("boom")
        ), patch.object(
            _module, "update_ecfr_result", return_value={"id": 7, "status": "failed"}
        ) as mock_update_result:
            with self.assertRaisesRegex(RuntimeError, "boom"):
                _module.handler({"body": "{}"}, None)

        self.assertEqual(mock_update_result.call_args.kwargs["result_id"], 7)
        self.assertEqual(mock_update_result.call_args.kwargs["payload"]["status"], "failed")
        self.assertIn("boom", mock_update_result.call_args.kwargs["payload"]["log"])


if __name__ == "__main__":
    unittest.main()
