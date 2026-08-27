import unittest
from importlib import util
from pathlib import Path
from unittest.mock import Mock, patch

import requests

from common.auth import BackendCredentials


def _load_module(module_name: str, relative_path: str):
    module_path = Path(__file__).resolve().parent.parent / "ecfr-worker" / relative_path
    spec = util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {relative_path} module")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_ecfr_client = _load_module("ecfr_worker_ecfr_client", "ecfr_client.py")
_eregs_client = _load_module("ecfr_worker_eregs_client", "eregs_client.py")


class EcfrWorkerClientsTests(unittest.TestCase):
    @patch("requests.get")
    def test_fetch_part_structure_success(self, mock_get):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"type": "title", "children": []}
        mock_get.return_value = response

        payload = _ecfr_client.fetch_part_structure(title_number=42, part_number=400)

        self.assertEqual(payload, {"type": "title", "children": []})
        self.assertEqual(mock_get.call_args.kwargs["params"], {"part": "400"})

    @patch("requests.get")
    def test_fetch_part_structure_non_2xx(self, mock_get):
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError(response=Mock(status_code=502))
        mock_get.return_value = response

        with self.assertRaisesRegex(_ecfr_client.EcfrClientError, "structure request failed"):
            _ecfr_client.fetch_part_structure(title_number=42, part_number=400)

    @patch("requests.get")
    def test_fetch_part_full_xml_success(self, mock_get):
        response = Mock()
        response.raise_for_status.return_value = None
        response.text = "<xml/>"
        mock_get.return_value = response

        xml_body = _ecfr_client.fetch_part_full_xml(title_number=42, part_number=400, effective_date="2025-01-01")

        self.assertEqual(xml_body, "<xml/>")
        self.assertEqual(mock_get.call_args.kwargs["params"], {"part": "400"})

    @patch("requests.put")
    def test_upload_part_success(self, mock_put):
        response = Mock()
        response.raise_for_status.return_value = None
        response.text = '{"ok": true}'
        response.json.return_value = {"ok": True}
        mock_put.return_value = response

        payload = {
            "name": "400",
            "title": "42",
            "date": "2025-01-01",
            "document": {},
            "structure": {},
            "depth": 0,
            "sections": [],
            "subparts": [],
        }

        result = _eregs_client.upload_part(
            api_base_url="https://example.local/v3/",
            credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
            payload=payload,
        )

        self.assertEqual(result, {"ok": True})
        headers = mock_put.call_args.kwargs["headers"]
        self.assertIn("Authorization", headers)
        self.assertEqual(headers["Content-Type"], "application/json")

    @patch("requests.put")
    def test_upload_part_non_2xx(self, mock_put):
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError(response=Mock(status_code=500))
        mock_put.return_value = response

        payload = {
            "name": "400",
            "title": "42",
            "date": "2025-01-01",
            "document": {},
            "structure": {},
            "depth": 0,
            "sections": [],
            "subparts": [],
        }

        with self.assertRaisesRegex(_eregs_client.EregsClientError, "upload failed"):
            _eregs_client.upload_part(
                api_base_url="https://example.local/v3/",
                credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
                payload=payload,
            )

    @patch("requests.post")
    def test_create_ecfr_result_success(self, mock_post):
        response = Mock()
        response.raise_for_status.return_value = None
        response.text = '{"id": 1}'
        response.json.return_value = {"id": 1}
        mock_post.return_value = response

        result = _eregs_client.create_ecfr_result(
            api_base_url="https://example.local/v3/",
            credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
            payload={
                "success": True,
                "log": "",
                "title": 42,
                "part": 400,
                "date": "2025-01-01",
            },
        )

        self.assertEqual(result, {"id": 1})
        self.assertTrue(mock_post.call_args.args[0].endswith("/parsers/ecfr/results"))

    @patch("requests.post")
    def test_create_ecfr_result_non_2xx(self, mock_post):
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError(response=Mock(status_code=500))
        mock_post.return_value = response

        with self.assertRaisesRegex(_eregs_client.EregsClientError, "result upload failed"):
            _eregs_client.create_ecfr_result(
                api_base_url="https://example.local/v3/",
                credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
                payload={
                    "success": False,
                    "log": "failure",
                    "title": 42,
                    "part": 400,
                    "date": "2025-01-01",
                },
            )

    @patch("requests.post")
    def test_increment_latest_ecfr_launcher_counter_success(self, mock_post):
        response = Mock()
        response.raise_for_status.return_value = None
        response.text = '{"abstractparserresult_ptr": 5, "succeeded_count": 1}'
        response.json.return_value = {"abstractparserresult_ptr": 5, "succeeded_count": 1}
        mock_post.return_value = response

        result = _eregs_client.increment_latest_ecfr_launcher_counter(
            api_base_url="https://example.local/v3/",
            credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
            counter="succeeded_count",
        )

        self.assertEqual(result["succeeded_count"], 1)
        self.assertTrue(mock_post.call_args.args[0].endswith("/parsers/ecfr-launcher/increment"))

    @patch("requests.post")
    def test_increment_latest_ecfr_launcher_counter_non_2xx(self, mock_post):
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError(response=Mock(status_code=500))
        mock_post.return_value = response

        with self.assertRaisesRegex(_eregs_client.EregsClientError, "counter increment failed"):
            _eregs_client.increment_latest_ecfr_launcher_counter(
                api_base_url="https://example.local/v3/",
                credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
                counter="failed_count",
            )

    def test_upload_part_missing_required_field(self):
        payload = {
            "name": "400",
            "title": "42",
            "date": "2025-01-01",
            "document": {},
            "structure": {},
            "depth": 0,
            "sections": [],
        }

        with self.assertRaisesRegex(_eregs_client.EregsClientError, "missing required fields"):
            _eregs_client.upload_part(
                api_base_url="https://example.local/v3/",
                credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
                payload=payload,
            )


if __name__ == "__main__":
    unittest.main()
