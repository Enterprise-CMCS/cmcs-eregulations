"""Shared HTTP request/response helpers for parser Lambda clients."""

from collections.abc import Callable
from typing import Any

import requests


def execute_request(
    request_call: Callable[[], requests.Response],
    *,
    on_http_error: Callable[[requests.HTTPError], Exception],
    on_request_error: Callable[[requests.RequestException], Exception],
) -> requests.Response:
    """Execute an HTTP request and map requests exceptions to domain errors."""

    try:
        response = request_call()
        response.raise_for_status()
        return response
    except requests.HTTPError as exc:
        raise on_http_error(exc) from exc
    except requests.RequestException as exc:
        raise on_request_error(exc) from exc


def parse_json_response(
    response: requests.Response,
    *,
    expected_type: type,
    on_invalid_json: Callable[[ValueError], Exception],
    on_invalid_shape: Callable[[], Exception],
) -> Any:
    """Parse and validate response JSON payload type."""

    try:
        payload = response.json()
    except ValueError as exc:
        raise on_invalid_json(exc) from exc

    if not isinstance(payload, expected_type):
        raise on_invalid_shape()

    return payload


def require_non_empty_text(
    response: requests.Response,
    *,
    on_empty: Callable[[], Exception],
) -> str:
    """Return response text when non-empty after trimming."""

    body = response.text
    if not isinstance(body, str) or not body.strip():
        raise on_empty()

    return body
