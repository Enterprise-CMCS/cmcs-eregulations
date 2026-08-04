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

    try:
        response = requests.get(request_url, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "unknown"
        raise EcfrVersionsError(f"eCFR versions request failed ({status_code}) for title {title_number}") from exc
    except requests.RequestException as exc:
        raise EcfrVersionsError(f"eCFR versions request failed for title {title_number}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise EcfrVersionsError(f"eCFR versions response was not valid JSON for title {title_number}") from exc

    if not isinstance(payload, dict):
        raise EcfrVersionsError(f"eCFR versions response must be a JSON object for title {title_number}")

    return payload


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

        part = item.get("part")
        if not isinstance(part, str) or not part.strip():
            continue
        part = part.strip()

        issue_date = _extract_issue_date(item)
        if issue_date is None:
            continue

        issue_date_value, issue_date_raw = issue_date
        existing = latest_by_part.get(part)
        if existing is None or issue_date_value > existing[0]:
            latest_by_part[part] = (issue_date_value, issue_date_raw)

    return {part: issue_date_raw for part, (_issue_date_value, issue_date_raw) in latest_by_part.items()}


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
