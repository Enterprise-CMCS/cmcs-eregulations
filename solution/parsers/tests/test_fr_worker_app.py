import json
import os
import sys
import unittest
from importlib import util
from pathlib import Path
from unittest.mock import patch

from common.auth import BackendCredentials


def _load_module():
    worker_dir = Path(__file__).resolve().parent.parent / "fr-worker"
    module_path = worker_dir / "app.py"

    import types

    package_name = "fr_worker_pkg"
    package = types.ModuleType(package_name)
    package.__path__ = [str(worker_dir)]
    sys.modules[package_name] = package

    spec = util.spec_from_file_location(f"{package_name}.app", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load fr worker app module")
    module = util.module_from_spec(spec)
    sys.modules[f"{package_name}.app"] = module
    spec.loader.exec_module(module)
    return module


_module = _load_module()
_config_spec = util.spec_from_file_location(
    "fr_worker_pkg.config",
    Path(__file__).resolve().parent.parent / "fr-worker" / "config.py",
)
if _config_spec is None or _config_spec.loader is None:
    raise RuntimeError("Unable to load fr worker config module")
_config_module = util.module_from_spec(_config_spec)
sys.modules["fr_worker_pkg.config"] = _config_module
_config_spec.loader.exec_module(_config_module)


class FrWorkerAppTests(unittest.TestCase):
    def test_handler_parses_config_and_returns_api_response(self):
        parsed_config = _config_module.FrDocumentConfig(
            document_number="2026-12345",
            credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
        )

        with patch.dict(os.environ, {}, clear=True), patch.object(_module, "parse_config_from_event", return_value=parsed_config):
            response = _module.handler({"body": "{}"}, None)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["headers"]["Content-Type"], "application/json")
        body = json.loads(response["body"])
        self.assertEqual(body["processed"], 1)
        self.assertEqual(body["document_number"], "2026-12345")


if __name__ == "__main__":
    unittest.main()
