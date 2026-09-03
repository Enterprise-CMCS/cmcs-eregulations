"""Parser-config retrieval and expansion helpers for the eCFR launcher.

This module adapts backend parser_config entries into normalized part targets
that can be turned into worker queue messages.
"""

from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import requests
from common.config import ConfigParseError, require_bool, require_non_empty_string, require_positive_int
from common.ecfr import (
    ECFR_V1_BASE_URL,
    fetch_subchapter_part_numbers,
    parse_part_number,
    parse_subchapter_value,
)
from common.eregs_config import EregsConfigError
from common.http import execute_request, parse_json_response

from common.auth import BackendCredentials, build_auth_headers


@dataclass(frozen=True)
class TargetPartConfig:
    """Normalized target part entry consumed by the launcher."""

    title_number: int
    part_number: int
    upload_reg_text: bool
    upload_locations: bool


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
            part_numbers = [parse_part_number(value)]
        elif item_type == "subchapter":
            chapter, subchapter = parse_subchapter_value(value)
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


def fetch_existing_part_dates_by_title(
    api_base_url: str,
    credentials: BackendCredentials,
    title_number: int,
    timeout: int = 60,
) -> dict[int, str]:
    """Fetch existing eRegs part dates for one title keyed by part number."""

    request_url = urljoin(api_base_url, f"title/{title_number}/parts")
    try:
        headers = build_auth_headers(credentials)
    except ConfigParseError as exc:
        raise EregsConfigError(str(exc)) from exc

    response = execute_request(
        lambda: requests.get(request_url, headers=headers, timeout=timeout),
        on_http_error=lambda exc: EregsConfigError(
            "eRegs title parts request failed "
            f"({exc.response.status_code if exc.response is not None else 'unknown'}) for title {title_number}"
        ),
        on_request_error=lambda exc: EregsConfigError(f"eRegs title parts request failed for title {title_number}: {exc}"),
    )

    payload = parse_json_response(
        response,
        expected_type=list,
        on_invalid_json=lambda _exc: EregsConfigError(f"eRegs title parts response was not valid JSON for title {title_number}"),
        on_invalid_shape=lambda: EregsConfigError("eRegs title parts response must be a JSON array"),
    )

    part_dates: dict[int, str] = {}
    for item in payload:
        if not isinstance(item, dict):
            continue

        name = item.get("name")
        date = item.get("date")
        if isinstance(name, str) and name.strip().isdigit() and isinstance(date, str) and date.strip():
            part_dates[int(name.strip())] = date.strip()

    return part_dates
