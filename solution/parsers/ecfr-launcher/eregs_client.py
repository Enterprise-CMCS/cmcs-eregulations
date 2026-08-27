"""HTTP client helpers for writing eCFR launcher run results to eRegs."""

from typing import Any
from urllib.parse import urljoin

import requests

from common.auth import BackendCredentials, build_auth_headers
from common.config import ConfigParseError
from common.http import execute_request, parse_json_response


class EregsClientError(RuntimeError):
    """Raised for failed eCFR launcher result requests or invalid payloads."""


def create_ecfr_launcher_result(
    api_base_url: str,
    credentials: BackendCredentials,
    payload: dict[str, Any],
    timeout: int = 60,
) -> dict[str, Any]:
    """Create one eCFR launcher result entry at /v3/parsers/ecfr/launcher-results."""

    request_url = urljoin(api_base_url, "parsers/ecfr/launcher-results")
    try:
        headers = build_auth_headers(credentials)
    except ConfigParseError as exc:
        raise EregsClientError(str(exc)) from exc

    headers["Content-Type"] = "application/json"

    response = execute_request(
        lambda: requests.post(request_url, json=payload, headers=headers, timeout=timeout),
        on_http_error=lambda exc: EregsClientError(
            "eRegs eCFR launcher result upload failed "
            f"({exc.response.status_code if exc.response is not None else 'unknown'})"
        ),
        on_request_error=lambda exc: EregsClientError(f"eRegs eCFR launcher result upload request failed: {exc}"),
    )

    if not response.text.strip():
        return {}

    return parse_json_response(
        response,
        expected_type=dict,
        on_invalid_json=lambda _exc: EregsClientError("eRegs eCFR launcher result upload response was not valid JSON"),
        on_invalid_shape=lambda: EregsClientError("eRegs eCFR launcher result upload response must be a JSON object"),
    )


def update_ecfr_launcher_result(
    api_base_url: str,
    credentials: BackendCredentials,
    payload: dict[str, Any],
    timeout: int = 60,
) -> dict[str, Any]:
    """Update the latest eCFR launcher result entry at /v3/parsers/ecfr/launcher-results."""

    request_url = urljoin(api_base_url, "parsers/ecfr/launcher-results")
    try:
        headers = build_auth_headers(credentials)
    except ConfigParseError as exc:
        raise EregsClientError(str(exc)) from exc

    headers["Content-Type"] = "application/json"

    response = execute_request(
        lambda: requests.patch(request_url, json=payload, headers=headers, timeout=timeout),
        on_http_error=lambda exc: EregsClientError(
            "eRegs eCFR launcher result update failed "
            f"({exc.response.status_code if exc.response is not None else 'unknown'})"
        ),
        on_request_error=lambda exc: EregsClientError(f"eRegs eCFR launcher result update request failed: {exc}"),
    )

    if not response.text.strip():
        return {}

    return parse_json_response(
        response,
        expected_type=dict,
        on_invalid_json=lambda _exc: EregsClientError("eRegs eCFR launcher result update response was not valid JSON"),
        on_invalid_shape=lambda: EregsClientError("eRegs eCFR launcher result update response must be a JSON object"),
    )
