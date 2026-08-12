import json
from datetime import date
from typing import Any
from urllib.parse import urljoin

import requests


ECFR_V1_BASE_URL = "https://www.ecfr.gov/api/versioner/v1/"


class EcfrVersionsError(RuntimeError):
    pass


def fetch_title_versions(
    title_number: int,
    base_url: str = ECFR_V1_BASE_URL,
    timeout: int = 60,
) -> dict[str, Any]:
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
    try:
        response = requests.get(request_url, timeout=timeout, params={"page": str(page)})
        response.raise_for_status()
        payload = response.json()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "unknown"
        raise EcfrVersionsError(
            f"eCFR versions request failed ({status_code}) for title {title_number} page {page}"
        ) from exc
    except requests.RequestException as exc:
        raise EcfrVersionsError(f"eCFR versions request failed for title {title_number} page {page}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise EcfrVersionsError(f"eCFR versions response was not valid JSON for title {title_number} page {page}") from exc

    if not isinstance(payload, dict):
        raise EcfrVersionsError(f"eCFR versions response must be a JSON object for title {title_number} page {page}")

    return payload


def _extract_total_pages(meta: Any) -> int:
    if not isinstance(meta, dict):
        return 1

    raw_total_pages = meta.get("total_pages", 1)
    if isinstance(raw_total_pages, int):
        return max(1, raw_total_pages)

    if isinstance(raw_total_pages, str) and raw_total_pages.strip().isdigit():
        return max(1, int(raw_total_pages.strip()))

    return 1


def latest_issue_dates_by_part(payload: dict[str, Any]) -> dict[str, str]:
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
    for key in ("issue_date", "date"):
        raw_value = item.get(key)
        parsed_value = _parse_date(raw_value)
        if parsed_value is not None and isinstance(raw_value, str):
            return parsed_value, raw_value.strip()[:10]
    return None


def _parse_date(value: Any) -> date | None:
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
