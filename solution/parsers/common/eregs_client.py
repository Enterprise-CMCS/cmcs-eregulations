"""Shared eRegs HTTP clients for parser Lambdas.

The eCFR launcher and worker both create and update per-part parser result rows
under /v3/parsers/ecfr/results. Because these calls are identical across both
Lambdas they live in the shared common package rather than being duplicated per
function. The generic send_json helper below captures the common authenticated
JSON request/response skeleton used across every parser eRegs client.
"""

from typing import Any
from urllib.parse import urljoin

import requests

from common.auth import BackendCredentials, build_auth_headers
from common.config import ConfigParseError
from common.http import execute_request, parse_json_response


class EregsClientError(RuntimeError):
    """Raised for failed eRegs parser client requests or invalid payloads."""


def send_json(
    api_base_url: str,
    verb: str,
    path: str,
    credentials: BackendCredentials,
    error_label: str,
    json_body: dict[str, Any] | None = None,
    expected_type: type = dict,
    timeout: int = 60,
) -> Any:
    """Send an authenticated JSON request to eRegs and parse the response.

    verb is one of "get", "post", "put", "patch". When json_body is provided the
    request carries a JSON body and the Content-Type header is set; an empty
    response body then yields {}. For body-less (GET) requests the response body
    is parsed as expected_type (dict or list).
    """

    request_url = urljoin(api_base_url, path)
    try:
        headers = build_auth_headers(credentials)
    except ConfigParseError as exc:
        raise EregsClientError(str(exc)) from exc

    method = getattr(requests, verb)
    kwargs: dict[str, Any] = {"headers": headers, "timeout": timeout}
    if json_body is not None:
        headers["Content-Type"] = "application/json"
        kwargs["json"] = json_body

    response = execute_request(
        lambda: method(request_url, **kwargs),
        on_http_error=lambda exc: EregsClientError(
            f"{error_label} failed ({exc.response.status_code if exc.response is not None else 'unknown'})"
        ),
        on_request_error=lambda exc: EregsClientError(f"{error_label} request failed: {exc}"),
    )

    if json_body is not None and not response.text.strip():
        return {}

    return parse_json_response(
        response,
        expected_type=expected_type,
        on_invalid_json=lambda _exc: EregsClientError(f"{error_label} response was not valid JSON"),
        on_invalid_shape=lambda: EregsClientError(f"{error_label} response must be a JSON object"),
    )


def create_ecfr_result(
    api_base_url: str,
    credentials: BackendCredentials,
    payload: dict[str, Any],
    timeout: int = 60,
) -> dict[str, Any]:
    """Create one eCFR parser result entry at /v3/parsers/ecfr/results."""

    return send_json(
        api_base_url,
        "post",
        "parsers/ecfr/results",
        credentials,
        "eRegs eCFR result upload",
        json_body=payload,
        timeout=timeout,
    )


def update_ecfr_result(
    api_base_url: str,
    credentials: BackendCredentials,
    result_id: int,
    payload: dict[str, Any],
    timeout: int = 60,
) -> dict[str, Any]:
    """Update one eCFR parser result entry at /v3/parsers/ecfr/results/<id>."""

    return send_json(
        api_base_url,
        "patch",
        f"parsers/ecfr/results/{result_id}",
        credentials,
        "eRegs eCFR result update",
        json_body=payload,
        timeout=timeout,
    )
