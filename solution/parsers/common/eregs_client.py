"""Shared eRegs HTTP clients for parser Lambdas.

The eCFR launcher and worker both create and update per-part parser result rows
under /v3/parsers/ecfr/results. Because these calls are identical across both
Lambdas they live in the shared common package rather than being duplicated per
function.
"""

from typing import Any
from urllib.parse import urljoin

import requests

from common.auth import BackendCredentials, build_auth_headers
from common.config import ConfigParseError
from common.http import execute_request, parse_json_response


class EregsClientError(RuntimeError):
    """Raised for failed eRegs parser client requests or invalid payloads."""


def create_ecfr_result(
    api_base_url: str,
    credentials: BackendCredentials,
    payload: dict[str, Any],
    timeout: int = 60,
) -> dict[str, Any]:
    """Create one eCFR parser result entry at /v3/parsers/ecfr/results."""

    request_url = urljoin(api_base_url, "parsers/ecfr/results")
    try:
        headers = build_auth_headers(credentials)
    except ConfigParseError as exc:
        raise EregsClientError(str(exc)) from exc

    headers["Content-Type"] = "application/json"

    response = execute_request(
        lambda: requests.post(request_url, json=payload, headers=headers, timeout=timeout),
        on_http_error=lambda exc: EregsClientError(
            f"eRegs eCFR result upload failed ({exc.response.status_code if exc.response is not None else 'unknown'})"
        ),
        on_request_error=lambda exc: EregsClientError(f"eRegs eCFR result upload request failed: {exc}"),
    )

    if not response.text.strip():
        return {}

    return parse_json_response(
        response,
        expected_type=dict,
        on_invalid_json=lambda _exc: EregsClientError("eRegs eCFR result upload response was not valid JSON"),
        on_invalid_shape=lambda: EregsClientError("eRegs eCFR result upload response must be a JSON object"),
    )


def update_ecfr_result(
    api_base_url: str,
    credentials: BackendCredentials,
    result_id: int,
    payload: dict[str, Any],
    timeout: int = 60,
) -> dict[str, Any]:
    """Update one eCFR parser result entry at /v3/parsers/ecfr/results/<id>."""

    request_url = urljoin(api_base_url, f"parsers/ecfr/results/{result_id}")
    try:
        headers = build_auth_headers(credentials)
    except ConfigParseError as exc:
        raise EregsClientError(str(exc)) from exc

    headers["Content-Type"] = "application/json"

    response = execute_request(
        lambda: requests.patch(request_url, json=payload, headers=headers, timeout=timeout),
        on_http_error=lambda exc: EregsClientError(
            f"eRegs eCFR result update failed ({exc.response.status_code if exc.response is not None else 'unknown'})"
        ),
        on_request_error=lambda exc: EregsClientError(f"eRegs eCFR result update request failed: {exc}"),
    )

    if not response.text.strip():
        return {}

    return parse_json_response(
        response,
        expected_type=dict,
        on_invalid_json=lambda _exc: EregsClientError("eRegs eCFR result update response was not valid JSON"),
        on_invalid_shape=lambda: EregsClientError("eRegs eCFR result update response must be a JSON object"),
    )
