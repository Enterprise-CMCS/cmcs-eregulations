"""HTTP client helpers for eCFR structure/full-document reads.

These calls are isolated from handler logic to keep orchestration testable and
to centralize API-specific error handling.
"""

from typing import Any
from urllib.parse import urljoin

import requests
from common.ecfr import ECFR_V1_BASE_URL
from common.http import execute_request, parse_json_response, require_non_empty_text


class EcfrClientError(RuntimeError):
    """Raised for failed or malformed eCFR API responses."""

    pass


def fetch_part_structure(
    title_number: int,
    part_number: int,
    timeout: int = 60,
    base_url: str = ECFR_V1_BASE_URL,
) -> dict[str, Any]:
    """Fetch current eCFR structure JSON for one title/part."""

    endpoint = f"structure/current/title-{title_number}.json"
    request_url = urljoin(base_url, endpoint)

    response = execute_request(
        lambda: requests.get(request_url, params={"part": str(part_number)}, timeout=timeout),
        on_http_error=lambda exc: EcfrClientError(
            f"eCFR structure request failed ({exc.response.status_code if exc.response is not None else 'unknown'}) "
            f"for title {title_number} part {part_number}"
        ),
        on_request_error=lambda exc: EcfrClientError(
            f"eCFR structure request failed for title {title_number} part {part_number}: {exc}"
        ),
    )

    payload = parse_json_response(
        response,
        expected_type=dict,
        on_invalid_json=lambda _exc: EcfrClientError(
            f"eCFR structure response was not valid JSON for title {title_number} part {part_number}"
        ),
        on_invalid_shape=lambda: EcfrClientError(
            f"eCFR structure response must be a JSON object for title {title_number} part {part_number}"
        ),
    )

    return payload


def fetch_part_full_xml(
    title_number: int,
    part_number: int,
    effective_date: str,
    timeout: int = 60,
    base_url: str = ECFR_V1_BASE_URL,
) -> str:
    """Fetch full XML for one title/part at a specific effective date."""

    endpoint = f"full/{effective_date}/title-{title_number}.xml"
    request_url = urljoin(base_url, endpoint)

    response = execute_request(
        lambda: requests.get(request_url, params={"part": str(part_number)}, timeout=timeout),
        on_http_error=lambda exc: EcfrClientError(
            f"eCFR full XML request failed ({exc.response.status_code if exc.response is not None else 'unknown'}) "
            f"for title {title_number} part {part_number} date {effective_date}"
        ),
        on_request_error=lambda exc: EcfrClientError(
            f"eCFR full XML request failed for title {title_number} part {part_number} date {effective_date}: {exc}"
        ),
    )

    return require_non_empty_text(
        response,
        on_empty=lambda: EcfrClientError(
            f"eCFR full XML response was empty for title {title_number} part {part_number} date {effective_date}"
        ),
    )
