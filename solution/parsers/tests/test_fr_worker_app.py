import json
import sys
import unittest
from importlib import util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from common.auth import BackendCredentials


def _load_links_module():
    mod = util.spec_from_file_location("links", WORKER_DIR.parent / "fr-worker" / "links.py")
    m = util.module_from_spec(mod)
    sys.modules["links"] = m
    mod.loader.exec_module(m)
    return m


def _load_module(module_name, package_name, worker_dir, filename):
    import types

    package = types.ModuleType(package_name)
    package.__path__ = [str(worker_dir)]
    sys.modules[package_name] = package

    module_path = worker_dir / filename
    spec = util.spec_from_file_location(f"{package_name}.{module_name}", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {filename} module")
    module = util.module_from_spec(spec)
    sys.modules[f"{package_name}.{module_name}"] = module
    spec.loader.exec_module(module)
    return module


WORKER_DIR = Path(__file__).resolve().parent.parent / "fr-worker"
LINKS = _load_links_module()
_module = _load_module("app", "fr_worker_pkg", WORKER_DIR, "app.py")


def _config(**overrides):
    base = {
        "document_number": "2026-12345",
        "title": 42,
        "part": "400",
        "description": "A document title",
        "name": "90 FR 1",
        "doc_type": "Rule",
        "url": "https://example/x",
        "date": "2026-01-01",
        "docket_numbers": ["ABC-1"],
        "raw_text_url": "https://example/x.txt",
        "full_text_xml_url": "https://example/x.xml",
        "log_level": "DEBUG",
        "credentials": BackendCredentials(auth_type="basic", username="u", password="p"),
    }
    base.update({k: v for k, v in overrides.items() if v is not None})
    return SimpleNamespace(**base)


class FrWorkerAppTests(unittest.TestCase):
    @patch("os.environ", {"EREGS_API_URL_V3": "https://example.local/"}, create=True)
    def test_handler_success_records_success_result(self):
        config = _config()
        link_section = LINKS.LinkSection(title="42", part="400", section_id=502)
        link_range = LINKS.LinkSectionRange(title="42", part="400", first_sec=502, last_sec=700)

        with (
            patch.object(_module, "parse_config_from_event", return_value=config),
            patch.object(_module, "_extract_linked_sections", return_value=([link_section], [link_range])),
            patch.object(_module, "upload_fr_document", return_value={"id": 1}),
            patch.object(_module, "create_fr_result") as mock_create,
        ):
            response = _module.handler({"body": "{}"}, None)

        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["processed"], 1)
        self.assertEqual(body["document_number"], "2026-12345")
        self.assertEqual(body["sections"], 1)
        self.assertEqual(body["section_ranges"], 1)
        self.assertTrue(body["uploaded"])

        mock_create.assert_called_once()
        payload = mock_create.call_args.kwargs["payload"]
        self.assertTrue(payload["success"])
        self.assertEqual(payload["document_number"], "2026-12345")

    @patch("os.environ", {"EREGS_API_URL_V3": "https://example.local/"}, create=True)
    def test_handler_failure_records_failure_result_and_reraises(self):
        config = _config()
        with (
            patch.object(_module, "parse_config_from_event", return_value=config),
            patch.object(_module, "_process_work_item", side_effect=RuntimeError("boom")),
            patch.object(_module, "create_fr_result") as mock_create,
        ):
            with self.assertRaisesRegex(RuntimeError, "boom"):
                _module.handler({"body": "{}"}, None)

        mock_create.assert_called_once()
        payload = mock_create.call_args.kwargs["payload"]
        self.assertFalse(payload["success"])
        self.assertEqual(payload["document_number"], "2026-12345")
        self.assertIn("boom", payload["log"])

    @patch("os.environ", {"EREGS_API_URL_V3": "https://example.local/"}, create=True)
    def test_extract_section_failure_still_uploads(self):
        config = _config()
        with (
            patch.object(_module, "parse_config_from_event", return_value=config),
            patch.object(_module, "_extract_linked_sections", side_effect=RuntimeError("xml down")),
            patch.object(_module, "upload_fr_document") as mock_upload,
            patch.object(_module, "create_fr_result"),
        ):
            _module.handler({"body": "{}"}, None)

        self.assertEqual(mock_upload.call_args.kwargs["payload"]["sections"], [])
        self.assertEqual(mock_upload.call_args.kwargs["payload"]["section_ranges"], [])


if __name__ == "__main__":
    unittest.main()
