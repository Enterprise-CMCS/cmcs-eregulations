from typing import Any
from urllib.parse import urljoin

import requests


ECFR_V1_BASE_URL = "https://www.ecfr.gov/api/versioner/v1/"


class EcfrClientError(RuntimeError):
    pass


def fetch_part_structure(
    title_number: int,
    part_number: int,
    timeout: int = 60,
    base_url: str = ECFR_V1_BASE_URL,
) -> dict[str, Any]:
    endpoint = f"structure/current/title-{title_number}.json"
    request_url = urljoin(base_url, endpoint)

    try:
        response = requests.get(request_url, params={"part": str(part_number)}, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "unknown"
        raise EcfrClientError(
            f"eCFR structure request failed ({status_code}) for title {title_number} part {part_number}"
        ) from exc
    except requests.RequestException as exc:
        raise EcfrClientError(f"eCFR structure request failed for title {title_number} part {part_number}: {exc}") from exc
    except ValueError as exc:
        raise EcfrClientError(
            f"eCFR structure response was not valid JSON for title {title_number} part {part_number}"
        ) from exc

    if not isinstance(payload, dict):
        raise EcfrClientError(
            f"eCFR structure response must be a JSON object for title {title_number} part {part_number}"
        )

    return payload


def fetch_part_full_xml(
    title_number: int,
    part_number: int,
    effective_date: str,
    timeout: int = 60,
    base_url: str = ECFR_V1_BASE_URL,
) -> str:
    endpoint = f"full/{effective_date}/title-{title_number}.xml"
    request_url = urljoin(base_url, endpoint)

    try:
        response = requests.get(request_url, params={"part": str(part_number)}, timeout=timeout)
        response.raise_for_status()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "unknown"
        raise EcfrClientError(
            f"eCFR full XML request failed ({status_code}) for title {title_number} part {part_number} date {effective_date}"
        ) from exc
    except requests.RequestException as exc:
        raise EcfrClientError(
            f"eCFR full XML request failed for title {title_number} part {part_number} date {effective_date}: {exc}"
        ) from exc

    xml_body = response.text
    if not isinstance(xml_body, str) or not xml_body.strip():
        raise EcfrClientError(
            f"eCFR full XML response was empty for title {title_number} part {part_number} date {effective_date}"
        )

    return xml_body
