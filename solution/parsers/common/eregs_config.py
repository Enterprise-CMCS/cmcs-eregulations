"""Shared eRegs parser-config retrieval helpers for launcher Lambdas."""

from typing import Any
from urllib.parse import urljoin

import requests

from common.auth import BackendCredentials, build_auth_headers
from common.config import ConfigParseError
from common.http import execute_request, parse_json_response


class EregsConfigError(RuntimeError):
    """Raised for parser-config request/validation failures."""


def fetch_parser_config(
    api_base_url: str,
    credentials: BackendCredentials,
    timeout: int = 60,
) -> dict[str, Any]:
    """Fetch parser configuration from the eRegs parsers/config endpoint."""

    request_url = urljoin(api_base_url, "parsers/config")
    try:
        headers = build_auth_headers(credentials)
    except ConfigParseError as exc:
        raise EregsConfigError(str(exc)) from exc

    response = execute_request(
        lambda: requests.get(request_url, headers=headers, timeout=timeout),
        on_http_error=lambda exc: EregsConfigError(
            f"eRegs parser_config request failed ({exc.response.status_code if exc.response is not None else 'unknown'})"
        ),
        on_request_error=lambda exc: EregsConfigError(f"eRegs parser_config request failed: {exc}"),
    )

    return parse_json_response(
        response,
        expected_type=dict,
        on_invalid_json=lambda _exc: EregsConfigError("eRegs parser_config response was not valid JSON"),
        on_invalid_shape=lambda: EregsConfigError("eRegs parser_config response must be a JSON object"),
    )
