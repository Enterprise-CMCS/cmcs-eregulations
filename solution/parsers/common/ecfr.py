"""Shared eCFR helpers for parser-config target expansion.

Both the eCFR launcher (part/subchapter targets) and the FR launcher
(subchapter targets for Federal Register discovery) expand configured titles
into concrete part lists by querying the eCFR structure API. This module
centralizes the base URL, the structure payload walk, and the parser-config
value parsing that both launchers depend on.
"""

from typing import Any
from urllib.parse import urljoin

import requests

from common.eregs_config import EregsConfigError
from common.http import execute_request, parse_json_response

ECFR_V1_BASE_URL = "https://www.ecfr.gov/api/versioner/v1/"


def fetch_subchapter_part_numbers(
    title_number: int,
    chapter: str,
    subchapter: str,
    timeout: int = 60,
    base_url: str = ECFR_V1_BASE_URL,
) -> list[int]:
    """Fetch all part numbers under one title/chapter/subchapter."""

    endpoint = f"structure/current/title-{title_number}.json"
    request_url = urljoin(base_url, endpoint)

    response = execute_request(
        lambda: requests.get(
            request_url,
            params={"chapter": chapter, "subchapter": subchapter},
            timeout=timeout,
        ),
        on_http_error=lambda exc: EregsConfigError(
            "eCFR subchapter structure request failed "
            f"({exc.response.status_code if exc.response is not None else 'unknown'}) "
            f"for title {title_number} {chapter}-{subchapter}"
        ),
        on_request_error=lambda exc: EregsConfigError(
            f"eCFR subchapter structure request failed for title {title_number} {chapter}-{subchapter}: {exc}"
        ),
    )

    payload = parse_json_response(
        response,
        expected_type=dict,
        on_invalid_json=lambda _exc: EregsConfigError(
            f"eCFR subchapter structure response was not valid JSON for title {title_number} {chapter}-{subchapter}"
        ),
        on_invalid_shape=lambda: EregsConfigError("eCFR subchapter structure response must be a JSON object"),
    )

    part_numbers = extract_part_numbers(payload)
    if not part_numbers:
        raise EregsConfigError(f"no parts found for title {title_number} subchapter {chapter}-{subchapter}")

    return part_numbers


def extract_part_numbers(node: Any) -> list[int]:
    """Walk structure payload and collect unique part identifiers."""

    part_numbers: set[int] = set()

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            node_type = value.get("type")
            if node_type == "part":
                identifier = value.get("identifier")
                parsed = identifier_to_part_number(identifier)
                if parsed is not None:
                    part_numbers.add(parsed)

            children = value.get("children")
            if isinstance(children, list):
                for child in children:
                    walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(node)
    return sorted(part_numbers)


def identifier_to_part_number(identifier: Any) -> int | None:
    """Convert eCFR identifier values to integer part numbers when possible."""

    if isinstance(identifier, str):
        candidate = identifier.strip()
        if candidate.isdigit():
            return int(candidate)
        return None

    if isinstance(identifier, list) and identifier:
        first = identifier[0]
        if isinstance(first, str) and first.strip().isdigit():
            return int(first.strip())

    return None


def parse_subchapter_value(value: str) -> tuple[str, str]:
    """Parse parser-config subchapter value in CHAPTER-SUBCHAPTER format."""

    pieces = value.split("-", 1)
    if len(pieces) != 2 or not pieces[0].strip() or not pieces[1].strip():
        raise EregsConfigError(f"invalid subchapter value '{value}', expected CHAPTER-SUBCHAPTER")
    return pieces[0].strip(), pieces[1].strip()


def parse_part_number(value: str) -> int:
    """Parse config part value as a numeric part entry."""

    if not value.strip().isdigit():
        raise EregsConfigError(f"invalid part value '{value}', expected numeric part")
    return int(value.strip())


__all__ = [
    "ECFR_V1_BASE_URL",
    "extract_part_numbers",
    "fetch_subchapter_part_numbers",
    "identifier_to_part_number",
    "parse_part_number",
    "parse_subchapter_value",
]
