"""Federal Register API client for discovering documents in the launcher.

The Federal Register documents API is public and does not require backend
credentials. It is paginated; callers follow the next_page_url chain to
collect the full result set for a title/part.
"""

from dataclasses import dataclass
from typing import Any

import requests
from common.fedreg import FedRegClientError
from common.http import execute_request, parse_json_response

FEDERAL_REGISTER_API_BASE_URL = "https://www.federalregister.gov"

# The Federal Register documents endpoint filtering by CFR title and part.
# Requesting the newest-first ordering keeps discovery deterministic.
_DOCUMENTS_ENDPOINT = "/api/v1/documents.json"

_REQUIRED_FIELDS = [
    "type",
    "full_text_xml_url",
    "citation",
    "docket_ids",
    "document_number",
    "html_url",
    "publication_date",
    "title",
    "raw_text_url",
]


@dataclass(frozen=True)
class FrDoc:
    """A Federal Register document as returned by the documents API."""

    name: str
    description: str
    category: str
    url: str
    date: str
    docket_numbers: list[str]
    document_number: str
    full_text_url: str
    raw_text_url: str


def fetch_documents(
    title: int,
    part: str,
    timeout: int = 60,
    base_url: str = FEDERAL_REGISTER_API_BASE_URL,
) -> list[FrDoc]:
    """Fetch all FR documents for one CFR title/part, following pagination."""

    start_url = _build_documents_url(title, part, base_url)
    return _fetch_page(start_url, timeout=timeout)


def _build_documents_url(title: int, part: str, base_url: str) -> str:
    params = {
        "fields[]": _REQUIRED_FIELDS,
        "order": "newest",
        "conditions[cfr][title]": str(title),
        "conditions[cfr][part]": part,
    }
    request = requests.Request("GET", base_url + _DOCUMENTS_ENDPOINT, params=params).prepare()
    return request.url


def _fetch_page(url: str, timeout: int) -> list[FrDoc]:
    response = execute_request(
        lambda: requests.get(url, timeout=timeout),
        on_http_error=lambda exc: FedRegClientError(
            f"Federal Register documents request failed ({exc.response.status_code if exc.response is not None else 'unknown'})"
        ),
        on_request_error=lambda exc: FedRegClientError(f"Federal Register documents request failed: {exc}"),
    )

    payload = parse_json_response(
        response,
        expected_type=dict,
        on_invalid_json=lambda _exc: FedRegClientError("Federal Register documents response was not valid JSON"),
        on_invalid_shape=lambda: FedRegClientError("Federal Register documents response must be a JSON object"),
    )

    docs = [_parse_doc(item) for item in payload.get("results", []) if isinstance(item, dict)]

    next_page_url = payload.get("next_page_url")
    if isinstance(next_page_url, str) and next_page_url:
        docs.extend(_fetch_page(next_page_url, timeout=timeout))

    return docs


def _parse_doc(item: dict[str, Any]) -> FrDoc:
    return FrDoc(
        name=str(item.get("citation", "") or ""),
        description=str(item.get("title", "") or ""),
        category=str(item.get("type", "") or ""),
        url=str(item.get("html_url", "") or ""),
        date=str(item.get("publication_date", "") or ""),
        docket_numbers=_parse_string_list(item.get("docket_ids")),
        document_number=str(item.get("document_number", "") or ""),
        full_text_url=str(item.get("full_text_xml_url", "") or ""),
        raw_text_url=str(item.get("raw_text_url", "") or ""),
    )


def _parse_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    return []
