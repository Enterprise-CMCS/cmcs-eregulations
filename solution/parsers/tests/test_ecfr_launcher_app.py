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
    def test_build_work_units_includes_effective_date_and_flags(self):
        targets = [
            _module.TargetPartConfig(
                title_number=42,
                part_number=400,
                upload_reg_text=True,
                upload_locations=False,
            )
        ]

        with patch.object(_module, "fetch_parser_config", return_value={"parts": []}), patch.object(
            _module, "expand_target_parts", return_value=targets
        ), patch.object(_module, "_resolve_latest_dates_by_title", return_value={42: {400: "2025-01-01"}}), patch.object(
            _module,
            "_resolve_existing_part_dates_by_title",
            return_value={42: {}},
        ):
            work_units, failures = _module._build_work_units(
                parser_config={
                    "parts": [],
                    "skip_parsed_regs": True,
                    "upload_supplemental_locations": True,
                },
                api_base_url="https://example.local/v3/",
                credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
                ecfr_api_base_url="https://ecfr.example/api/versioner/v1/",
                parser_log_level="INFO",
            )

        self.assertEqual(failures, [])
        self.assertEqual(
            work_units,
            [
                {
                    "config": {
                        "title_number": 42,
                        "part_number": 400,
                        "effective_date": "2025-01-01",
                        "upload_reg_text": True,
                        "upload_locations": False,
                        "log_level": "INFO",
                    }
                }
            ],
        )

    def test_build_work_units_records_missing_latest_date_failure(self):
        targets = [
            _module.TargetPartConfig(
                title_number=42,
                part_number=400,
                upload_reg_text=True,
                upload_locations=True,
            )
        ]

        with patch.object(_module, "fetch_parser_config", return_value={"parts": []}), patch.object(
            _module, "expand_target_parts", return_value=targets
        ), patch.object(_module, "_resolve_latest_dates_by_title", return_value={42: {}}), patch.object(
            _module,
            "_resolve_existing_part_dates_by_title",
            return_value={42: {}},
        ):
            work_units, failures = _module._build_work_units(
                parser_config={
                    "parts": [],
                    "skip_parsed_regs": True,
                    "upload_supplemental_locations": True,
                },
                api_base_url="https://example.local/v3/",
                credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
                ecfr_api_base_url="https://ecfr.example/api/versioner/v1/",
                parser_log_level="WARNING",
            )

        self.assertEqual(work_units, [])
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0]["title_number"], "42")
        self.assertEqual(failures[0]["part_number"], "400")

    def test_resolve_latest_dates_by_title_uses_one_versions_call_per_title(self):
        targets = [
            _module.TargetPartConfig(42, 400, True, True),
            _module.TargetPartConfig(42, 401, True, True),
            _module.TargetPartConfig(43, 10, True, True),
        ]

        with patch.object(_module, "fetch_title_versions") as fetch_versions, patch.object(
            _module,
            "latest_issue_dates_by_part",
            side_effect=[
                {"400": "2025-01-01", "401": "2025-01-02"},
                {"10": "2025-02-01"},
            ],
        ):
            resolved = _module._resolve_latest_dates_by_title(targets, "https://ecfr.example/api/versioner/v1/")

        self.assertEqual(fetch_versions.call_count, 2)
        called_titles = sorted(call.kwargs["title_number"] for call in fetch_versions.call_args_list)
        self.assertEqual(called_titles, [42, 43])
        self.assertEqual(
            resolved,
            {
                42: {400: "2025-01-01", 401: "2025-01-02"},
                43: {10: "2025-02-01"},
            },
        )

    def test_handler_merges_config_and_dispatch_failures(self):
        with patch.dict(
            "os.environ",
            {
                "EREGS_API_URL_V3": "https://example.local/v3/",
                "PARSER_LOCAL_MODE": "true",
            },
            clear=True,
        ), patch.object(
            _module, "resolve_backend_credentials", return_value=BackendCredentials(auth_type="basic", username="u", password="p")
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
            "_resolve_parser_log_level",
            return_value="INFO",
        ), patch.object(
            _module,
            "_build_work_units",
            return_value=(
                [
                    {
                        "config": {
                            "title_number": 42,
                            "part_number": 400,
                            "effective_date": "2025-01-01",
                            "log_level": "INFO",
                        }
                    }
                ],
                [{"title_number": "42", "part_number": "401", "reason": "No latest issue_date available for part"}],
            ),
        ), patch.object(
            _module,
            "dispatch_work_units",
            return_value=(
                True,
                1,
                [{"index": "0", "reason": "simulated dispatch issue"}],
            ),
        ):
            response = _module.handler({"body": "{}"}, None)

        body = json.loads(response["body"])
        self.assertEqual(body["enqueued"], 1)
        self.assertEqual(body["succeeded"], 1)
        self.assertEqual(body["failed"], 2)
        self.assertEqual(len(body["failures"]), 2)

    def test_resolve_parser_log_level_from_parser_config(self):
        self.assertEqual(_module._resolve_parser_log_level({"loglevel": "warn"}), "WARNING")
        self.assertEqual(_module._resolve_parser_log_level({"loglevel": "trace"}), "DEBUG")

    def test_resolve_parser_log_level_rejects_invalid_value(self):
        with self.assertRaisesRegex(RuntimeError, "loglevel must be one of"):
            _module._resolve_parser_log_level({"loglevel": "verbose"})

    def test_build_work_units_skips_when_existing_date_matches_latest(self):
        targets = [
            _module.TargetPartConfig(
                title_number=42,
                part_number=400,
                upload_reg_text=True,
                upload_locations=True,
            )
        ]

        with patch.object(_module, "expand_target_parts", return_value=targets), patch.object(
            _module,
            "_resolve_latest_dates_by_title",
            return_value={42: {400: "2025-01-01"}},
        ), patch.object(
            _module,
            "_resolve_existing_part_dates_by_title",
            return_value={42: {400: "2025-01-01"}},
        ):
            work_units, failures = _module._build_work_units(
                parser_config={
                    "parts": [],
                    "skip_parsed_regs": True,
                    "upload_supplemental_locations": True,
                },
                api_base_url="https://example.local/v3/",
                credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
                ecfr_api_base_url="https://ecfr.example/api/versioner/v1/",
                parser_log_level="INFO",
            )

        self.assertEqual(work_units, [])
        self.assertEqual(failures, [])

    def test_build_work_units_does_not_skip_when_skip_parsed_regs_false(self):
        targets = [
            _module.TargetPartConfig(
                title_number=42,
                part_number=400,
                upload_reg_text=True,
                upload_locations=True,
            )
        ]

        with patch.object(_module, "expand_target_parts", return_value=targets), patch.object(
            _module,
            "_resolve_latest_dates_by_title",
            return_value={42: {400: "2025-01-01"}},
        ), patch.object(
            _module,
            "_resolve_existing_part_dates_by_title",
        ) as mock_existing:
            work_units, failures = _module._build_work_units(
                parser_config={
                    "parts": [],
                    "skip_parsed_regs": False,
                    "upload_supplemental_locations": True,
                },
                api_base_url="https://example.local/v3/",
                credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
                ecfr_api_base_url="https://ecfr.example/api/versioner/v1/",
                parser_log_level="INFO",
            )

        self.assertEqual(len(work_units), 1)
        self.assertEqual(failures, [])
        mock_existing.assert_not_called()

    def test_resolve_skip_parsed_regs_from_parser_config(self):
        self.assertTrue(_module._resolve_skip_parsed_regs({"skip_parsed_regs": True}))
        self.assertFalse(_module._resolve_skip_parsed_regs({"skip_parsed_regs": False}))

    def test_resolve_skip_parsed_regs_rejects_invalid_value(self):
        with self.assertRaisesRegex(RuntimeError, "skip_parsed_regs must be a boolean"):
            _module._resolve_skip_parsed_regs({"skip_parsed_regs": "yes"})

    def test_build_work_units_forces_upload_locations_false_when_global_disabled(self):
        targets = [
            _module.TargetPartConfig(
                title_number=42,
                part_number=400,
                upload_reg_text=True,
                upload_locations=True,
            )
        ]

        with patch.object(_module, "expand_target_parts", return_value=targets), patch.object(
            _module,
            "_resolve_latest_dates_by_title",
            return_value={42: {400: "2025-01-01"}},
        ), patch.object(
            _module,
            "_resolve_existing_part_dates_by_title",
            return_value={42: {}},
        ):
            work_units, failures = _module._build_work_units(
                parser_config={
                    "parts": [],
                    "skip_parsed_regs": True,
                    "upload_supplemental_locations": False,
                },
                api_base_url="https://example.local/v3/",
                credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
                ecfr_api_base_url="https://ecfr.example/api/versioner/v1/",
                parser_log_level="INFO",
            )

        self.assertEqual(failures, [])
        self.assertEqual(len(work_units), 1)
        self.assertFalse(work_units[0]["config"]["upload_locations"])

    def test_resolve_upload_supplemental_locations_from_parser_config(self):
        self.assertTrue(_module._resolve_upload_supplemental_locations({"upload_supplemental_locations": True}))
        self.assertFalse(_module._resolve_upload_supplemental_locations({"upload_supplemental_locations": False}))

    def test_resolve_upload_supplemental_locations_rejects_invalid_value(self):
        with self.assertRaisesRegex(RuntimeError, "upload_supplemental_locations must be a boolean"):
            _module._resolve_upload_supplemental_locations({"upload_supplemental_locations": "yes"})


if __name__ == "__main__":
    unittest.main()
