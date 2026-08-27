import unittest
from importlib import util
from pathlib import Path
from unittest.mock import Mock, patch

import requests

from common.auth import BackendCredentials


def _load_module():
    module_path = Path(__file__).resolve().parent.parent / "ecfr-launcher" / "eregs_client.py"
    spec = util.spec_from_file_location("ecfr_launcher_eregs_client", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load ecfr launcher eregs_client module")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_module = _load_module()


class EcfrLauncherClientTests(unittest.TestCase):
    @patch("requests.post")
    def test_create_ecfr_launcher_result_success(self, mock_post):
        response = Mock()
        response.raise_for_status.return_value = None
        response.text = '{"id": 1}'
        response.json.return_value = {"id": 1}
        mock_post.return_value = response

        result = _module.create_ecfr_launcher_result(
            api_base_url="https://example.local/v3/",
            credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
            payload={"success": True, "log": ""},
        )

        self.assertEqual(result, {"id": 1})
        self.assertTrue(mock_post.call_args.args[0].endswith("/parsers/ecfr/launcher-results"))

    @patch("requests.post")
    def test_create_ecfr_launcher_result_non_2xx(self, mock_post):
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError(response=Mock(status_code=500))
        mock_post.return_value = response

        with self.assertRaisesRegex(_module.EregsClientError, "launcher result upload failed"):
            _module.create_ecfr_launcher_result(
                api_base_url="https://example.local/v3/",
                credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
                payload={"success": False, "log": "boom"},
            )


if __name__ == "__main__":
    unittest.main()
