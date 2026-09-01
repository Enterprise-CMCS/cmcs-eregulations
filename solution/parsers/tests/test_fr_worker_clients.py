import unittest
from importlib import util
from pathlib import Path
from unittest.mock import Mock, patch

import requests
from common.eregs_client import EregsClientError

from common.auth import BackendCredentials


def _load_module(module_name: str, relative_path: str):
    module_path = Path(__file__).resolve().parent.parent / "fr-worker" / relative_path
    spec = util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {relative_path} module")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_eregs_client = _load_module("fr_worker_eregs_client", "eregs_client.py")

_VALID = {
    "name": "a citation",
    "description": "a title",
    "doc_type": "Rule",
    "url": "https://gov.example/x",
    "date": "2025-01-31",
    "document_number": "2025-12345",
    "sections": [{"title": "42", "part": "400", "section_id": 502}],
    "section_ranges": [],
    "docket_numbers": ["CMS-0000-F2"],
    "raw_text_url": "https://gov.example/x.txt",
}


class FrWorkerClientsTests(unittest.TestCase):
    @patch("requests.put")
    def test_upload_fr_document_success(self, mock_put):
        response = Mock()
        response.raise_for_status.return_value = None
        response.text = '{"document_number": "2025-12345"}'
        response.json.return_value = {"document_number": "2025-12345"}
        mock_put.return_value = response

        result = _eregs_client.upload_fr_document(
            api_base_url="https://example.local/",
            credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
            payload=dict(_VALID),
        )

        self.assertEqual(result, {"document_number": "2025-12345"})
        self.assertTrue(mock_put.call_args.args[0].endswith("/resources/public/federal_register_links"))
        headers = mock_put.call_args.kwargs["headers"]
        self.assertIn("Authorization", headers)
        self.assertEqual(headers["Content-Type"], "application/json")

    @patch("requests.put")
    def test_upload_fr_document_non_2xx(self, mock_put):
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError(response=Mock(status_code=500))
        mock_put.return_value = response

        with self.assertRaisesRegex(EregsClientError, "upload failed"):
            _eregs_client.upload_fr_document(
                api_base_url="https://example.local/",
                credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
                payload=dict(_VALID),
            )

    def test_upload_fr_document_missing_required_field(self):
        payload = {k: v for k, v in _VALID.items() if k != "document_number"}

        with self.assertRaisesRegex(EregsClientError, "missing required fields"):
            _eregs_client.upload_fr_document(
                api_base_url="https://example.local/",
                credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
                payload=payload,
            )

    @patch("requests.post")
    def test_create_fr_result_success(self, mock_post):
        response = Mock()
        response.raise_for_status.return_value = None
        response.text = '{"document_number": "2025-12345"}'
        response.json.return_value = {"document_number": "2025-12345"}
        mock_post.return_value = response

        result = _eregs_client.create_fr_result(
            api_base_url="https://example.local/",
            credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
            payload={"success": True, "log": "", "document_number": "2025-12345"},
        )

        self.assertEqual(result, {"document_number": "2025-12345"})
        self.assertTrue(mock_post.call_args.args[0].endswith("/parsers/fr/results"))

    @patch("requests.post")
    def test_create_fr_result_non_2xx(self, mock_post):
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError(response=Mock(status_code=500))
        mock_post.return_value = response

        with self.assertRaisesRegex(EregsClientError, "result upload failed"):
            _eregs_client.create_fr_result(
                api_base_url="https://example.local/",
                credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
                payload={"success": False, "log": "failure", "document_number": "2025-12345"},
            )


if __name__ == "__main__":
    unittest.main()
