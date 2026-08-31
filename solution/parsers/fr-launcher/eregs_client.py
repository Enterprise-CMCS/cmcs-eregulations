"""HTTP client helpers for the Federal Register launcher.

Reads the list of already-processed FR document numbers from eRegs (for
deduplication) and writes Federal Register launcher run results.
"""

from typing import Any
from urllib.parse import urljoin

import requests
from common.config import ConfigParseError
from common.eregs_client import EregsClientError
from common.http import execute_request, parse_json_response

from common.auth import BackendCredentials, build_auth_headers


def fetch_existing_document_numbers(
    api_base_url: str,
    credentials: BackendCredentials,
    timeout: int = 60,
) -> list[str]:
    """Fetch all document numbers eRegs already stores for FR links."""

    request_url = urljoin(api_base_url, "resources/public/federal_register_links/document_numbers")
    try:
        headers = build_auth_headers(credentials)
    except ConfigParseError as exc:
        raise EregsClientError(str(exc)) from exc

    response = execute_request(
        lambda: requests.get(request_url, headers=headers, timeout=timeout),
        on_http_error=lambda exc: EregsClientError(
            "eRegs FR document list request failed "
            f"({exc.response.status_code if exc.response is not None else 'unknown'})"
        ),
        on_request_error=lambda exc: EregsClientError(f"eRegs FR document list request failed: {exc}"),
    )

    payload = parse_json_response(
        response,
        expected_type=list,
        on_invalid_json=lambda _exc: EregsClientError("eRegs FR document list response was not valid JSON"),
        on_invalid_shape=lambda: EregsClientError("eRegs FR document list response must be a JSON array"),
    )

    return [str(item) for item in payload]


def create_fr_launcher_result(
    api_base_url: str,
    credentials: BackendCredentials,
    payload: dict[str, Any],
    timeout: int = 60,
) -> dict[str, Any]:
    """Create one Federal Register launcher result at /v3/parsers/fr/launcher-results."""

    request_url = urljoin(api_base_url, "parsers/fr/launcher-results")
    try:
        headers = build_auth_headers(credentials)
    except ConfigParseError as exc:
        raise EregsClientError(str(exc)) from exc

    headers["Content-Type"] = "application/json"

    response = execute_request(
        lambda: requests.post(request_url, json=payload, headers=headers, timeout=timeout),
        on_http_error=lambda exc: EregsClientError(
            "eRegs FR launcher result upload failed "
            f"({exc.response.status_code if exc.response is not None else 'unknown'})"
        ),
        on_request_error=lambda exc: EregsClientError(f"eRegs FR launcher result upload request failed: {exc}"),
    )

    if not response.text.strip():
        return {}

    return parse_json_response(
        response,
        expected_type=dict,
        on_invalid_json=lambda _exc: EregsClientError("eRegs FR launcher result upload response was not valid JSON"),
        on_invalid_shape=lambda: EregsClientError("eRegs FR launcher result upload response must be a JSON object"),
    )


def update_fr_launcher_result(
    api_base_url: str,
    credentials: BackendCredentials,
    payload: dict[str, Any],
    timeout: int = 60,
) -> dict[str, Any]:
    """Update the latest Federal Register launcher result at /v3/parsers/fr/launcher-results."""

    request_url = urljoin(api_base_url, "parsers/fr/launcher-results")
    try:
        headers = build_auth_headers(credentials)
    except ConfigParseError as exc:
        raise EregsClientError(str(exc)) from exc

    headers["Content-Type"] = "application/json"

    response = execute_request(
        lambda: requests.patch(request_url, json=payload, headers=headers, timeout=timeout),
        on_http_error=lambda exc: EregsClientError(
            "eRegs FR launcher result update failed "
            f"({exc.response.status_code if exc.response is not None else 'unknown'})"
        ),
        on_request_error=lambda exc: EregsClientError(f"eRegs FR launcher result update request failed: {exc}"),
    )

    if not response.text.strip():
        return {}

    return parse_json_response(
        response,
        expected_type=dict,
        on_invalid_json=lambda _exc: EregsClientError("eRegs FR launcher result update response was not valid JSON"),
        on_invalid_shape=lambda: EregsClientError("eRegs FR launcher result update response must be a JSON object"),
    )
