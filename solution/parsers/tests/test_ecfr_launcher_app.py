import json
import sys
import types
import unittest
from importlib import util
from pathlib import Path
from unittest.mock import patch

from common.auth import BackendCredentials


def _load_module():
    launcher_dir = Path(__file__).resolve().parent.parent / "ecfr-launcher"
    module_path = launcher_dir / "app.py"

    package_name = "ecfr_launcher_pkg"
    package = types.ModuleType(package_name)
    package.__path__ = [str(launcher_dir)]
    sys.modules[package_name] = package

    spec = util.spec_from_file_location(f"{package_name}.app", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load ecfr launcher app module")
    module = util.module_from_spec(spec)
    sys.modules[f"{package_name}.app"] = module
    spec.loader.exec_module(module)
    return module


_module = _load_module()


class EcfrLauncherAppTests(unittest.TestCase):
    def test_build_work_units_includes_ids_and_flags(self):
        targets = [
            _module.TargetPartConfig(
                title_number=42,
                part_number=400,
                upload_reg_text=True,
                upload_locations=False,
            )
        ]

        with patch.object(_module, "expand_target_parts", return_value=targets), patch.object(
            _module, "_resolve_latest_dates_by_title", return_value={42: {400: "2025-01-01"}}
        ), patch.object(
            _module,
            "_resolve_existing_part_dates_by_title",
            return_value={42: {}},
        ), patch.object(
            _module,
            "create_ecfr_result",
            return_value={"abstractparserresult_ptr": 77},
        ) as mock_create:
            work_units, skipped_count = _module._build_work_units(
                parser_config={
                    "parts": [],
                    "skip_parsed_regs": True,
                    "upload_supplemental_locations": True,
                },
                api_base_url="https://example.local/v3/",
                credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
                ecfr_api_base_url="https://ecfr.example/api/versioner/v1/",
                parser_log_level="INFO",
                launcher_result_id=10,
            )

        self.assertEqual(skipped_count, 0)
        self.assertEqual(len(work_units), 1)
        self.assertEqual(work_units[0]["config"]["parser_result_id"], 77)
        self.assertEqual(work_units[0]["config"]["launcher_result_id"], 10)
        self.assertEqual(work_units[0]["config"]["upload_locations"], False)

        payload = mock_create.call_args.kwargs["payload"]
        self.assertEqual(payload["status"], "queued")
        self.assertFalse(payload["success"])

    def test_build_work_units_records_skipped_rows(self):
        targets = [
            _module.TargetPartConfig(42, 400, True, True),
            _module.TargetPartConfig(42, 401, True, True),
        ]

        with patch.object(_module, "expand_target_parts", return_value=targets), patch.object(
            _module, "_resolve_latest_dates_by_title", return_value={42: {401: "2025-01-01"}}
        ), patch.object(
            _module,
            "_resolve_existing_part_dates_by_title",
            return_value={42: {401: "2025-01-01"}},
        ), patch.object(
            _module,
            "create_ecfr_result",
            return_value={"abstractparserresult_ptr": 1},
        ) as mock_create:
            work_units, skipped_count = _module._build_work_units(
                parser_config={
                    "parts": [],
                    "skip_parsed_regs": True,
                    "upload_supplemental_locations": True,
                },
                api_base_url="https://example.local/v3/",
                credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
                ecfr_api_base_url="https://ecfr.example/api/versioner/v1/",
                parser_log_level="INFO",
                launcher_result_id=10,
            )

        self.assertEqual(work_units, [])
        self.assertEqual(skipped_count, 2)
        self.assertEqual(mock_create.call_count, 2)

    def test_handler_creates_launcher_then_updates_summary(self):
        with patch.dict(
            "os.environ",
            {
                "EREGS_API_URL_V3": "https://example.local/v3/",
                "PARSER_LOCAL_MODE": "true",
            },
            clear=True,
        ), patch.object(
            _module,
            "resolve_backend_credentials",
            return_value=BackendCredentials(auth_type="basic", username="u", password="p"),
        ), patch.object(
            _module,
            "fetch_parser_config",
            return_value={
                "parts": [],
                "loglevel": "info",
                "skip_parsed_regs": True,
                "upload_supplemental_locations": True,
            },
        ), patch.object(
            _module,
            "create_ecfr_launcher_result",
            return_value={"abstractparserresult_ptr": 50},
        ), patch.object(
            _module,
            "_build_work_units",
            return_value=(
                [{"config": {"parser_result_id": 7, "launcher_result_id": 50, "title_number": 42, "part_number": 400}}],
                1,
            ),
        ), patch.object(
            _module,
            "dispatch_work_units",
            return_value=(True, 1, []),
        ), patch.object(
            _module,
            "update_ecfr_launcher_result",
            return_value={"abstractparserresult_ptr": 50},
        ) as mock_update:
            response = _module.handler({"body": "{}"}, None)

        body = json.loads(response["body"])
        self.assertEqual(body["enqueued"], 1)
        self.assertEqual(body["failed"], 0)
        self.assertIn("queued=1 skipped=1", mock_update.call_args.kwargs["payload"]["log"])


if __name__ == "__main__":
    unittest.main()
