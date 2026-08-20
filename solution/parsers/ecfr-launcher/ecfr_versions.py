"""eCFR versions API helpers used by the launcher planning step.

The launcher uses this module to fetch full title versions (all pages) and
derive the latest effective date per part before queueing worker messages.
"""

from datetime import date
from typing import Any
from urllib.parse import urljoin

import requests

from common.http import execute_request, parse_json_response


ECFR_V1_BASE_URL = "https://www.ecfr.gov/api/versioner/v1/"


class EcfrVersionsError(RuntimeError):
    """Raised for invalid or failed eCFR versions API responses."""

    pass


def fetch_title_versions(
    title_number: int,
    base_url: str = ECFR_V1_BASE_URL,
    timeout: int = 60,
) -> dict[str, Any]:
    """Fetch and merge all versions pages for a single eCFR title."""

    endpoint = f"versions/title-{title_number}"
    request_url = urljoin(base_url, endpoint)
    all_content_versions: list[Any] = []
    page = 1
    total_pages = 1

    while page <= total_pages:
        payload = _request_versions_page(
            title_number=title_number,
            request_url=request_url,
            timeout=timeout,
            page=page,
        )

        content_versions = payload.get("content_versions")
        if not isinstance(content_versions, list):
            raise EcfrVersionsError("eCFR versions response must include content_versions array")
        all_content_versions.extend(content_versions)

        meta = payload.get("meta")
        if page == 1:
            total_pages = _extract_total_pages(meta)

        page += 1

    return {
        "content_versions": all_content_versions,
    }


def _request_versions_page(
    title_number: int,
    request_url: str,
    timeout: int,
    page: int,
) -> dict[str, Any]:
    """Fetch a single page of eCFR versions data."""

    response = execute_request(
        lambda: requests.get(request_url, timeout=timeout, params={"page": str(page)}),
        on_http_error=lambda exc: EcfrVersionsError(
            f"eCFR versions request failed ({exc.response.status_code if exc.response is not None else 'unknown'}) "
            f"for title {title_number} page {page}"
        ),
        on_request_error=lambda exc: EcfrVersionsError(
            f"eCFR versions request failed for title {title_number} page {page}: {exc}"
        ),
    )

    return parse_json_response(
        response,
        expected_type=dict,
        on_invalid_json=lambda _exc: EcfrVersionsError(
            f"eCFR versions response was not valid JSON for title {title_number} page {page}"
        ),
        on_invalid_shape=lambda: EcfrVersionsError(
            f"eCFR versions response must be a JSON object for title {title_number} page {page}"
        ),
    )


def _extract_total_pages(meta: Any) -> int:
    """Extract total pages from versions response metadata."""

    if not isinstance(meta, dict):
        return 1

    raw_total_pages = meta.get("total_pages", 1)
    if isinstance(raw_total_pages, int):
        return max(1, raw_total_pages)

    if isinstance(raw_total_pages, str) and raw_total_pages.strip().isdigit():
        return max(1, int(raw_total_pages.strip()))

    return 1


def latest_issue_dates_by_part(payload: dict[str, Any]) -> dict[str, str]:
    """Build a part->latest-date map from merged versions payload data."""

    content_versions = payload.get("content_versions")
    if not isinstance(content_versions, list):
        raise EcfrVersionsError("eCFR versions response must include content_versions array")

    latest_by_part: dict[str, tuple[date, str]] = {}

    for item in content_versions:
        if not isinstance(item, dict):
            continue

        if item.get("removed") is True:
            continue

        part = _normalize_part_key(item.get("part"))
        if part is None:
            continue

        issue_date = _extract_issue_date(item)
        if issue_date is None:
            continue

        issue_date_value, issue_date_raw = issue_date
        existing = latest_by_part.get(part)
        if existing is None or issue_date_value > existing[0]:
            latest_by_part[part] = (issue_date_value, issue_date_raw)

    return {part: issue_date_raw for part, (_issue_date_value, issue_date_raw) in latest_by_part.items()}


def _normalize_part_key(value: Any) -> str | None:
    """Normalize part keys from eCFR payload into comparable numeric strings."""

    if isinstance(value, int):
        return str(value) if value > 0 else None

    if isinstance(value, float):
        if value.is_integer() and value > 0:
            return str(int(value))
        return None

    if isinstance(value, str):
        candidate = value.strip()
        if candidate.isdigit():
            return candidate
        return None

    if isinstance(value, list) and value:
        return _normalize_part_key(value[0])

    return None


def _extract_issue_date(item: dict[str, Any]) -> tuple[date, str] | None:
    """Extract and parse issue_date, falling back to date when needed."""

    for key in ("issue_date", "date"):
        raw_value = item.get(key)
        parsed_value = _parse_date(raw_value)
        if parsed_value is not None and isinstance(raw_value, str):
            return parsed_value, raw_value.strip()[:10]
    return None


def _parse_date(value: Any) -> date | None:
    """Parse ISO date-like values and return date objects for comparison."""

    if not isinstance(value, str):
        return None

    candidate = value.strip()
    if not candidate:
        return None

    candidate = candidate[:10]
    try:
        return date.fromisoformat(candidate)
    except ValueError:
        return None
