"""HTTP client helpers for the Federal Register launcher.

Reads the list of already-processed FR document numbers from eRegs (for
deduplication) and writes Federal Register launcher run results.
"""

from typing import Any

from common.eregs_client import send_json

from common.auth import BackendCredentials


def fetch_existing_document_numbers(
    api_base_url: str,
    credentials: BackendCredentials,
    timeout: int = 60,
) -> list[str]:
    """Fetch all document numbers eRegs already stores for FR links."""

    payload = send_json(
        api_base_url,
        "get",
        "resources/public/federal_register_links/document_numbers",
        credentials,
        "eRegs FR document list request",
        expected_type=list,
        timeout=timeout,
    )

    return [str(item) for item in payload]


def create_fr_launcher_result(
    api_base_url: str,
    credentials: BackendCredentials,
    payload: dict[str, Any],
    timeout: int = 60,
) -> dict[str, Any]:
    """Create one Federal Register launcher result at /v3/parsers/fr/launcher-results."""

    return send_json(
        api_base_url,
        "post",
        "parsers/fr/launcher-results",
        credentials,
        "eRegs FR launcher result upload",
        json_body=payload,
        timeout=timeout,
    )
