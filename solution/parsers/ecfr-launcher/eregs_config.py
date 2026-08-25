"""Parser-config retrieval and expansion helpers for the eCFR launcher.

This module adapts backend parser_config entries into normalized part targets
that can be turned into worker queue messages.
"""

from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import requests

from common.auth import BackendCredentials, build_auth_headers
from common.config import ConfigParseError, require_bool, require_non_empty_string, require_positive_int
from common.http import execute_request, parse_json_response


ECFR_V1_BASE_URL = "https://www.ecfr.gov/api/versioner/v1/"


class EregsConfigError(RuntimeError):
    """Raised for invalid parser-config data or expansion failures."""

    pass


@dataclass(frozen=True)
class TargetPartConfig:
    """Normalized target part entry consumed by the launcher."""

    title_number: int
    part_number: int
    upload_reg_text: bool
    upload_locations: bool


def fetch_parser_config(
    api_base_url: str,
    credentials: BackendCredentials,
    timeout: int = 60,
) -> dict[str, Any]:
    """Fetch parser configuration from eRegs backend."""

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


def expand_target_parts(
    parser_config: dict[str, Any],
    timeout: int = 60,
    ecfr_base_url: str = ECFR_V1_BASE_URL,
) -> list[TargetPartConfig]:
    """Expand parser_config entries into concrete (title, part) targets.

    Supports both direct part entries and subchapter expansion via eCFR
    structure/current endpoints.
    """

    raw_parts = parser_config.get("parts")
    if not isinstance(raw_parts, list):
        raise EregsConfigError("parser_config must include a parts array")

    targets: list[TargetPartConfig] = []
    seen: set[tuple[int, int, bool, bool]] = set()

    for item in raw_parts:
        if not isinstance(item, dict):
            raise EregsConfigError("each parser_config part entry must be a JSON object")

        try:
            title_number = require_positive_int(item, "title")
            item_type = require_non_empty_string(item, "type").lower()
            value = require_non_empty_string(item, "value")
            upload_reg_text = require_bool(item, "upload_reg_text")
            upload_locations = require_bool(item, "upload_locations")
        except ConfigParseError as exc:
            raise EregsConfigError(str(exc)) from exc

        if item_type == "part":
            part_numbers = [_parse_part_number(value)]
        elif item_type == "subchapter":
            chapter, subchapter = _parse_subchapter_value(value)
            part_numbers = fetch_subchapter_part_numbers(
                title_number=title_number,
                chapter=chapter,
                subchapter=subchapter,
                timeout=timeout,
                base_url=ecfr_base_url,
            )
        else:
            raise EregsConfigError(f"unsupported part type '{item_type}'")

        for part_number in part_numbers:
            key = (title_number, part_number, upload_reg_text, upload_locations)
            if key in seen:
                continue
            seen.add(key)
            targets.append(
                TargetPartConfig(
                    title_number=title_number,
                    part_number=part_number,
                    upload_reg_text=upload_reg_text,
                    upload_locations=upload_locations,
                )
            )

    return targets


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

    part_numbers = _extract_part_numbers(payload)
    if not part_numbers:
        raise EregsConfigError(f"no parts found for title {title_number} subchapter {chapter}-{subchapter}")

    return part_numbers


def _extract_part_numbers(node: Any) -> list[int]:
    """Walk structure payload and collect unique part identifiers."""

    part_numbers: set[int] = set()

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            node_type = value.get("type")
            if node_type == "part":
                identifier = value.get("identifier")
                parsed = _identifier_to_part_number(identifier)
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


def _identifier_to_part_number(identifier: Any) -> int | None:
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


def _parse_subchapter_value(value: str) -> tuple[str, str]:
    """Parse parser-config subchapter value in CHAPTER-SUBCHAPTER format."""

    pieces = value.split("-", 1)
    if len(pieces) != 2 or not pieces[0].strip() or not pieces[1].strip():
        raise EregsConfigError(f"invalid subchapter value '{value}', expected CHAPTER-SUBCHAPTER")
    return pieces[0].strip(), pieces[1].strip()


def _parse_part_number(value: str) -> int:
    """Parse parser-config part value as an integer."""

    if not value.strip().isdigit():
        raise EregsConfigError(f"invalid part value '{value}', expected numeric part")
    return int(value.strip())
