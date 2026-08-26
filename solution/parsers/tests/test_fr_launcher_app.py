import json
import sys
import unittest
from importlib import util
from pathlib import Path
from unittest.mock import patch

from common.auth import BackendCredentials


def _load_module():
    launcher_dir = Path(__file__).resolve().parent.parent / "fr-launcher"
    module_path = launcher_dir / "app.py"

    import types

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


class FrLauncherAppTests(unittest.TestCase):
    def test_handler_builds_and_dispatches_work_units(self):
        with patch.object(_module, "resolve_backend_credentials", return_value=BackendCredentials("basic", "u", "p", None)), patch.object(
            _module,
            "fetch_parser_config",
            return_value={"parts": [], "loglevel": "warn"},
        ), patch.object(
            _module,
            "_resolve_parser_log_level",
            return_value="WARNING",
        ), patch.object(
            _module, "dispatch_work_units", return_value=(True, 1, [])
        ) as mock_dispatch:
            with patch.dict("os.environ", {"EREGS_API_URL_V3": "https://example.local/v3/"}, clear=True):
                response = _module.handler({"body": "{}"}, None)

        body = json.loads(response["body"])
        self.assertEqual(body["enqueued"], 1)
        self.assertEqual(body["succeeded"], 1)
        self.assertEqual(body["failed"], 0)
        self.assertEqual(len(body["work_units"]), 1)
        self.assertIn("document_number", body["work_units"][0]["config"])
        self.assertEqual(body["work_units"][0]["config"]["log_level"], "WARNING")

        dispatch_payload = mock_dispatch.call_args.args[0]
        self.assertEqual(dispatch_payload, body["work_units"])

    def test_resolve_parser_log_level_from_parser_config(self):
        self.assertEqual(_module._resolve_parser_log_level({"loglevel": "warn"}), "WARNING")
        self.assertEqual(_module._resolve_parser_log_level({"loglevel": "trace"}), "DEBUG")

    def test_resolve_parser_log_level_rejects_invalid_value(self):
        with self.assertRaisesRegex(RuntimeError, "loglevel must be one of"):
            _module._resolve_parser_log_level({"loglevel": "verbose"})


if __name__ == "__main__":
    unittest.main()
