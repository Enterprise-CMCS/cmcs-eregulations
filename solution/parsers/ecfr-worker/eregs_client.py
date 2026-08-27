"""HTTP client helpers for uploading parsed part payloads to eRegs.

The eCFR worker builds normalized part payloads and delegates outbound upload
behavior to this module.
"""

from typing import Any
from urllib.parse import urljoin

import requests

from common.auth import BackendCredentials, build_auth_headers
from common.config import ConfigParseError
from common.http import execute_request, parse_json_response


class EregsClientError(RuntimeError):
    """Raised for failed part upload requests or invalid payloads."""

    pass


REQUIRED_PART_FIELDS = (
    "name",
    "title",
    "date",
    "document",
    "structure",
    "depth",
    "sections",
    "subparts",
)


def upload_part(
    api_base_url: str,
    credentials: BackendCredentials,
    payload: dict[str, Any],
    timeout: int = 60,
) -> dict[str, Any]:
    """Upload one parsed part payload to eRegs /v3/parsers/ecfr/parts."""

    _validate_part_payload(payload)

    request_url = urljoin(api_base_url, "parsers/ecfr/parts")
    try:
        headers = build_auth_headers(credentials)
    except ConfigParseError as exc:
        raise EregsClientError(str(exc)) from exc

    headers["Content-Type"] = "application/json"

    response = execute_request(
        lambda: requests.put(request_url, json=payload, headers=headers, timeout=timeout),
        on_http_error=lambda exc: EregsClientError(
            f"eRegs part upload failed ({exc.response.status_code if exc.response is not None else 'unknown'})"
        ),
        on_request_error=lambda exc: EregsClientError(f"eRegs part upload request failed: {exc}"),
    )

    if not response.text.strip():
        return {}

    return parse_json_response(
        response,
        expected_type=dict,
        on_invalid_json=lambda _exc: EregsClientError("eRegs part upload response was not valid JSON"),
        on_invalid_shape=lambda: EregsClientError("eRegs part upload response must be a JSON object"),
    )


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


def _validate_part_payload(payload: Any) -> None:
    """Validate required top-level keys for part upload payloads."""

    if not isinstance(payload, dict):
        raise EregsClientError("part upload payload must be a JSON object")

    missing = [field for field in REQUIRED_PART_FIELDS if field not in payload]
    if missing:
        raise EregsClientError(f"part upload payload missing required fields: {', '.join(missing)}")
