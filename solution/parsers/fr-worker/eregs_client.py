"""HTTP client helpers for uploading Federal Register documents to eRegs.

The FR worker builds a FederalRegisterLink payload (document metadata plus
extracted section/range locations) and PUTs it to eRegs. It also posts per
document parser results under the parsers FR results endpoint. Shared
EregsClientError lives in common.eregs_client.
"""

from typing import Any
from urllib.parse import urljoin

import requests
from common.config import ConfigParseError
from common.eregs_client import EregsClientError
from common.http import execute_request, parse_json_response

from common.auth import BackendCredentials, build_auth_headers

REQUIRED_DOCUMENT_FIELDS = (
    "name",
    "description",
    "doc_type",
    "url",
    "date",
    "document_number",
)


def upload_fr_document(
    api_base_url: str,
    credentials: BackendCredentials,
    payload: dict[str, Any],
    timeout: int = 60,
) -> dict[str, Any]:
    """Upload one Federal Register document payload to eRegs."""

    _validate_document_payload(payload)

    request_url = urljoin(api_base_url, "resources/public/federal_register_links")
    try:
        headers = build_auth_headers(credentials)
    except ConfigParseError as exc:
        raise EregsClientError(str(exc)) from exc

    headers["Content-Type"] = "application/json"

    response = execute_request(
        lambda: requests.put(request_url, json=payload, headers=headers, timeout=timeout),
        on_http_error=lambda exc: EregsClientError(
            f"eRegs Federal Register document upload failed "
            f"({exc.response.status_code if exc.response is not None else 'unknown'})"
        ),
        on_request_error=lambda exc: EregsClientError(
            f"eRegs Federal Register document upload request failed: {exc}"
        ),
    )

    if not response.text.strip():
        return {}

    return parse_json_response(
        response,
        expected_type=dict,
        on_invalid_json=lambda _exc: EregsClientError(
            "eRegs Federal Register document upload response was not valid JSON"
        ),
        on_invalid_shape=lambda: EregsClientError(
            "eRegs Federal Register document upload response must be a JSON object"
        ),
    )


def create_fr_result(
    api_base_url: str,
    credentials: BackendCredentials,
    payload: dict[str, Any],
    timeout: int = 60,
) -> dict[str, Any]:
    """Create one Federal Register parser result entry at /v3/parsers/fr/results."""

    request_url = urljoin(api_base_url, "parsers/fr/results")
    try:
        headers = build_auth_headers(credentials)
    except ConfigParseError as exc:
        raise EregsClientError(str(exc)) from exc

    headers["Content-Type"] = "application/json"

    response = execute_request(
        lambda: requests.post(request_url, json=payload, headers=headers, timeout=timeout),
        on_http_error=lambda exc: EregsClientError(
            f"eRegs FR result upload failed ({exc.response.status_code if exc.response is not None else 'unknown'})"
        ),
        on_request_error=lambda exc: EregsClientError(f"eRegs FR result upload request failed: {exc}"),
    )

    if not response.text.strip():
        return {}

    return parse_json_response(
        response,
        expected_type=dict,
        on_invalid_json=lambda _exc: EregsClientError("eRegs FR result upload response was not valid JSON"),
        on_invalid_shape=lambda: EregsClientError("eRegs FR result upload response must be a JSON object"),
    )


def _validate_document_payload(payload: Any) -> None:
    """Validate required top-level keys for Federal Register document uploads."""

    if not isinstance(payload, dict):
        raise EregsClientError("Federal Register document payload must be a JSON object")

    missing = [field for field in REQUIRED_DOCUMENT_FIELDS if field not in payload]
    if missing:
        raise EregsClientError(
            f"Federal Register document payload missing required fields: {', '.join(missing)}"
        )
