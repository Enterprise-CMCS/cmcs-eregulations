import unittest
from importlib import util
from pathlib import Path
from unittest.mock import Mock, patch

import requests
from common.eregs_client import EregsClientError

from common.auth import BackendCredentials


def _load_fedreg_client():
    module_path = Path(__file__).resolve().parent.parent / "fr-launcher" / "fedreg_client.py"
    spec = util.spec_from_file_location("fr_launcher_fedreg_client", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load fr launcher fedreg_client module")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_eregs_client():
    module_path = Path(__file__).resolve().parent.parent / "fr-launcher" / "eregs_client.py"
    spec = util.spec_from_file_location("fr_launcher_eregs_client", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load fr launcher eregs_client module")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_fedreg = _load_fedreg_client()
_eregs = _load_eregs_client()


def _response(payload: dict):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = payload
    return response


class FrLauncherFedRegClientTests(unittest.TestCase):
    @patch("requests.get")
    def test_fetch_documents_single_page(self, mock_get):
        payload = {
            "next_page_url": None,
            "results": [
                {
                    "citation": "90 FR 1",
                    "title": "A doc",
                    "type": "Rule",
                    "html_url": "https://example/a",
                    "publication_date": "2026-01-01",
                    "docket_ids": ["ABC-1", "DEF-2"],
                    "document_number": "2026-0001",
                    "full_text_xml_url": "https://example/a.xml",
                    "raw_text_url": "https://example/raw.txt",
                }
            ],
        }
        mock_get.return_value = _response(payload)

        docs = _fedreg.fetch_documents(title=42, part="400")

        self.assertEqual(len(docs), 1)
        doc = docs[0]
        self.assertEqual(doc.document_number, "2026-0001")
        self.assertEqual(doc.name, "90 FR 1")
        self.assertEqual(doc.docket_numbers, ["ABC-1", "DEF-2"])
        self.assertEqual(doc.full_text_url, "https://example/a.xml")
        mock_get.assert_called_once()
        self.assertIn("conditions%5Bcfr%5D%5Btitle%5D=42", mock_get.call_args.args[0])
        self.assertIn("conditions%5Bcfr%5D%5Bpart%5D=400", mock_get.call_args.args[0])

    @patch("requests.get")
    def test_fetch_documents_paginates(self, mock_get):
        page1 = _response(
            {
                "next_page_url": "https://example/?page=2",
                "results": [{"document_number": "2026-0001"}],
            }
        )
        page2 = _response(
            {
                "next_page_url": None,
                "results": [{"document_number": "2026-0002"}, {"document_number": "2026-0003"}],
            }
        )
        mock_get.side_effect = [page1, page2]

        docs = _fedreg.fetch_documents(title=42, part="400")

        self.assertEqual([d.document_number for d in docs], ["2026-0001", "2026-0002", "2026-0003"])
        self.assertEqual(mock_get.call_count, 2)

    @patch("requests.get")
    def test_fetch_documents_skips_non_object_results(self, mock_get):
        page1 = _response(
            {
                "next_page_url": None,
                "results": ["garbage", 42, {"document_number": "2026-0001"}],
            }
        )
        mock_get.return_value = page1

        docs = _fedreg.fetch_documents(title=42, part="400")

        self.assertEqual([d.document_number for d in docs], ["2026-0001"])

    @patch("requests.get")
    def test_fetch_documents_http_error(self, mock_get):
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError(response=Mock(status_code=500))
        mock_get.return_value = response

        with self.assertRaisesRegex(_fedreg.FedRegClientError, "documents request failed"):
            _fedreg.fetch_documents(title=42, part="400")


class FrLauncherEregsClientTests(unittest.TestCase):
    @patch("requests.get")
    def test_fetch_existing_document_numbers(self, mock_get):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = ["2026-0001", "2026-0002"]
        mock_get.return_value = response

        docs = _eregs.fetch_existing_document_numbers(
            api_base_url="https://example.local/v3/",
            credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
        )

        self.assertEqual(docs, ["2026-0001", "2026-0002"])
        url = mock_get.call_args.args[0]
        self.assertTrue(url.endswith("/resources/public/federal_register_links/document_numbers"))

    @patch("requests.get")
    def test_fetch_existing_document_numbers_http_error(self, mock_get):
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError(response=Mock(status_code=500))
        mock_get.return_value = response

        with self.assertRaisesRegex(EregsClientError, "document list request failed"):
            _eregs.fetch_existing_document_numbers(
                api_base_url="https://example.local/v3/",
                credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
            )

    @patch("requests.post")
    def test_create_fr_launcher_result_success(self, mock_post):
        response = Mock()
        response.raise_for_status.return_value = None
        response.text = '{"abstractparserresult_ptr": 1}'
        response.json.return_value = {"abstractparserresult_ptr": 1}
        mock_post.return_value = response

        result = _eregs.create_fr_launcher_result(
            api_base_url="https://example.local/v3/",
            credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
            payload={"success": True, "log": ""},
        )

        self.assertEqual(result, {"abstractparserresult_ptr": 1})
        self.assertTrue(mock_post.call_args.args[0].endswith("/parsers/fr/launcher-results"))

    @patch("requests.post")
    def test_create_fr_launcher_result_non_2xx(self, mock_post):
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError(response=Mock(status_code=500))
        mock_post.return_value = response

        with self.assertRaisesRegex(EregsClientError, "launcher result upload failed"):
            _eregs.create_fr_launcher_result(
                api_base_url="https://example.local/v3/",
                credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
                payload={"success": False, "log": "boom"},
            )

    @patch("requests.patch")
    def test_update_fr_launcher_result_success(self, mock_patch):
        response = Mock()
        response.raise_for_status.return_value = None
        response.text = '{"abstractparserresult_ptr": 1, "log": "queued=2 skipped=1"}'
        response.json.return_value = {"abstractparserresult_ptr": 1, "log": "queued=2 skipped=1"}
        mock_patch.return_value = response

        result = _eregs.update_fr_launcher_result(
            api_base_url="https://example.local/v3/",
            credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
            payload={"success": True, "log": "queued=2 skipped=1"},
        )

        self.assertEqual(result["log"], "queued=2 skipped=1")
        self.assertTrue(mock_patch.call_args.args[0].endswith("/parsers/fr/launcher-results"))

    @patch("requests.patch")
    def test_update_fr_launcher_result_non_2xx(self, mock_patch):
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError(response=Mock(status_code=500))
        mock_patch.return_value = response

        with self.assertRaisesRegex(EregsClientError, "launcher result update failed"):
            _eregs.update_fr_launcher_result(
                api_base_url="https://example.local/v3/",
                credentials=BackendCredentials(auth_type="basic", username="u", password="p"),
                payload={"success": True, "log": "queued=2 skipped=1"},
            )


if __name__ == "__main__":
    unittest.main()
