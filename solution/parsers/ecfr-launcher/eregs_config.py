from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import requests

from common.auth import BackendCredentials, build_auth_headers
from common.config import ConfigParseError, require_bool, require_non_empty_string, require_positive_int


ECFR_V1_BASE_URL = "https://www.ecfr.gov/api/versioner/v1/"


class EregsConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class TargetPartConfig:
    title_number: int
    part_number: int
    upload_reg_text: bool
    upload_locations: bool


def fetch_parser_config(
    api_base_url: str,
    credentials: BackendCredentials,
    timeout: int = 60,
) -> dict[str, Any]:
    request_url = urljoin(api_base_url, "parser_config")
    try:
        headers = build_auth_headers(credentials)
    except ConfigParseError as exc:
        raise EregsConfigError(str(exc)) from exc

    try:
        response = requests.get(request_url, headers=headers, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "unknown"
        raise EregsConfigError(f"eRegs parser_config request failed ({status_code})") from exc
    except requests.RequestException as exc:
        raise EregsConfigError(f"eRegs parser_config request failed: {exc}") from exc
    except ValueError as exc:
        raise EregsConfigError("eRegs parser_config response was not valid JSON") from exc

    if not isinstance(payload, dict):
        raise EregsConfigError("eRegs parser_config response must be a JSON object")

    return payload


def expand_target_parts(
    parser_config: dict[str, Any],
    timeout: int = 60,
    ecfr_base_url: str = ECFR_V1_BASE_URL,
) -> list[TargetPartConfig]:
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
    endpoint = f"structure/current/title-{title_number}.json"
    request_url = urljoin(base_url, endpoint)

    try:
        response = requests.get(
            request_url,
            params={"chapter": chapter, "subchapter": subchapter},
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "unknown"
        raise EregsConfigError(
            f"eCFR subchapter structure request failed ({status_code}) for title {title_number} {chapter}-{subchapter}"
        ) from exc
    except requests.RequestException as exc:
        raise EregsConfigError(
            f"eCFR subchapter structure request failed for title {title_number} {chapter}-{subchapter}: {exc}"
        ) from exc
    except ValueError as exc:
        raise EregsConfigError(
            f"eCFR subchapter structure response was not valid JSON for title {title_number} {chapter}-{subchapter}"
        ) from exc

    if not isinstance(payload, dict):
        raise EregsConfigError("eCFR subchapter structure response must be a JSON object")

    part_numbers = _extract_part_numbers(payload)
    if not part_numbers:
        raise EregsConfigError(f"no parts found for title {title_number} subchapter {chapter}-{subchapter}")

    return part_numbers


def _extract_part_numbers(node: Any) -> list[int]:
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
    pieces = value.split("-", 1)
    if len(pieces) != 2 or not pieces[0].strip() or not pieces[1].strip():
        raise EregsConfigError(f"invalid subchapter value '{value}', expected CHAPTER-SUBCHAPTER")
    return pieces[0].strip(), pieces[1].strip()


def _parse_part_number(value: str) -> int:
    if not value.strip().isdigit():
        raise EregsConfigError(f"invalid part value '{value}', expected numeric part")
    return int(value.strip())
