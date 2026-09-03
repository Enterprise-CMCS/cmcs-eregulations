import json
import sys
import types
import unittest
from importlib import util
from pathlib import Path
from unittest.mock import patch

import requests

from common.auth import BackendCredentials


def _load_module():
    launcher_dir = Path(__file__).resolve().parent.parent / "fr-launcher"
    module_path = launcher_dir / "app.py"

    package_name = "fr_launcher_pkg"
    package = types.ModuleType(package_name)
    package.__path__ = [str(launcher_dir)]
    sys.modules[package_name] = package

    spec = util.spec_from_file_location(f"{package_name}.app", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load fr launcher app module")
    module = util.module_from_spec(spec)
    sys.modules[f"{package_name}.app"] = module
    spec.loader.exec_module(module)
    return module


_module = _load_module()


def _doc(document_number, **kwargs):
    defaults = {
        "name": "90 FR 1",
        "description": "A document",
        "category": "Rule",
        "url": "https://example/x",
        "date": "2026-01-01",
        "docket_numbers": [],
        "full_text_url": "https://example/x.xml",
        "raw_text_url": "https://example/x.txt",
    }
    defaults.update(kwargs)
    return _module.FrDoc(document_number=document_number, **defaults)


class FrLauncherAppTests(unittest.TestCase):
    def test_resolve_parser_log_level_from_parser_config(self):
        self.assertEqual(_module.resolve_parser_log_level({"loglevel": "warn"}), "WARNING")
        self.assertEqual(_module.resolve_parser_log_level({"loglevel": "trace"}), "DEBUG")

    def test_resolve_parser_log_level_rejects_invalid_value(self):
        with self.assertRaisesRegex(RuntimeError, "loglevel must be one of"):
            _module.resolve_parser_log_level({"loglevel": "verbose"})

    def test_build_work_units_skip_disabled_queues_all_docs(self):
        targets = [_module.FrTarget(title_number=42, part_number=400)]
        docs = [_doc("2026-0001"), _doc("2026-0002")]

        with patch.object(_module, "expand_fr_targets", return_value=targets), patch.object(
            _module, "_resolve_skip_fr_documents", return_value=False
        ), patch.object(
            _module, "fetch_documents", return_value=docs
        ):
            work_units, skipped_count = _module._build_work_units(
                parser_config={},
                api_base_url="https://example.local/v3/",
                credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
                parser_log_level="INFO",
                ecfr_api_base_url="https://ecfr.example/api/versioner/v1/",
                fr_api_base_url="https://www.federalregister.gov",
            )

        self.assertEqual([w["config"]["document_number"] for w in work_units], ["2026-0001", "2026-0002"])
        self.assertEqual(skipped_count, 0)
        cfg = work_units[0]["config"]
        self.assertEqual(cfg["title"], 42)
        self.assertEqual(cfg["part"], "400")
        self.assertEqual(cfg["log_level"], "INFO")

    def test_build_work_units_dedupes_when_skip_fr_documents(self):
        targets = [_module.FrTarget(title_number=42, part_number=400)]
        docs = [_doc("2026-0001"), _doc("2026-0002"), _doc("2026-0003")]

        with patch.object(_module, "expand_fr_targets", return_value=targets), patch.object(
            _module, "_resolve_skip_fr_documents", return_value=True
        ), patch.object(
            _module, "fetch_existing_document_numbers", return_value=["2026-0002"]
        ), patch.object(
            _module, "fetch_documents", return_value=docs
        ):
            work_units, skipped_count = _module._build_work_units(
                parser_config={},
                api_base_url="https://example.local/v3/",
                credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
                parser_log_level="INFO",
                ecfr_api_base_url="https://ecfr.example/api/versioner/v1/",
                fr_api_base_url="https://www.federalregister.gov",
            )

        self.assertEqual([w["config"]["document_number"] for w in work_units], ["2026-0001", "2026-0003"])
        self.assertEqual(skipped_count, 1)

    def test_handler_dispatches_and_records_launcher_result(self):
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
                "skip_fr_documents": True,
            },
        ), patch.object(
            _module,
            "_build_work_units",
            return_value=([{"config": {"document_number": "2026-0001"}}], 2),
        ), patch.object(
            _module,
            "dispatch_work_units",
            return_value=(True, 1, []),
        ), patch.object(
            _module,
            "create_fr_launcher_result",
        ) as mock_create:
            response = _module.handler({"body": "{}"}, None)

        body = json.loads(response["body"])
        self.assertEqual(body["enqueued"], 1)
        self.assertEqual(body["succeeded"], 1)

        payload = mock_create.call_args.kwargs["payload"]
        self.assertTrue(payload["success"])
        self.assertEqual(payload["queued_count"], 1)
        self.assertEqual(payload["skipped_count"], 2)
        self.assertEqual(payload["failed_count"], 0)

    def test_handler_records_failure_result_on_error(self):
        with patch.dict(
            "os.environ",
            {
                "EREGS_API_URL_V3": "https://example.local/v3/",
            },
            clear=True,
        ), patch.object(
            _module,
            "resolve_backend_credentials",
            return_value=BackendCredentials(auth_type="basic", username="u", password="p"),
        ), patch.object(
            _module,
            "fetch_parser_config",
            return_value={"parts": [], "loglevel": "info"},
        ), patch.object(
            _module,
            "_build_work_units",
            side_effect=requests.HTTPError("boom"),
        ), patch.object(
            _module,
            "create_fr_launcher_result",
        ) as mock_create:
            with self.assertRaises(requests.HTTPError):
                _module.handler({"body": "{}"}, None)

        payload = mock_create.call_args.kwargs["payload"]
        self.assertFalse(payload["success"])
        self.assertIn("boom", payload["log"])


if __name__ == "__main__":
    unittest.main()
