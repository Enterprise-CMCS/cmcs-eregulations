"""Federal Register parser-config retrieval and target expansion.

Adapts backend parser_config entries into normalized FR (title, part)
targets for which the launcher should discover Federal Register documents.
Only entries with upload_fr_docs enabled are expanded.
"""

from dataclasses import dataclass
from typing import Any

from common.config import ConfigParseError, require_bool, require_non_empty_string, require_positive_int
from common.ecfr import (
    ECFR_V1_BASE_URL,
    fetch_subchapter_part_numbers,
    parse_part_number,
    parse_subchapter_value,
)
from common.eregs_config import EregsConfigError


@dataclass(frozen=True)
class FrTarget:
    """A normalized (title, part) pair for which FR docs are requested."""

    title_number: int
    part_number: int


def expand_fr_targets(
    parser_config: dict[str, Any],
    timeout: int = 60,
    ecfr_base_url: str = ECFR_V1_BASE_URL,
) -> list[FrTarget]:
    """Expand upload_fr_docs-enabled parser_config entries into targets.

    Supports both direct part entries and subchapter expansion via the eCFR
    structure endpoint. Targets are deduplicated across entries.
    """

    raw_parts = parser_config.get("parts")
    if not isinstance(raw_parts, list):
        raise EregsConfigError("parser_config must include a parts array")

    targets: list[FrTarget] = []
    seen: set[tuple[int, int]] = set()

    for item in raw_parts:
        if not isinstance(item, dict):
            raise EregsConfigError("each parser_config part entry must be a JSON object")

        try:
            title_number = require_positive_int(item, "title")
            item_type = require_non_empty_string(item, "type").lower()
            value = require_non_empty_string(item, "value")
            upload_fr_docs = require_bool(item, "upload_fr_docs")
        except ConfigParseError as exc:
            raise EregsConfigError(str(exc)) from exc

        if not upload_fr_docs:
            continue

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
            key = (title_number, part_number)
            if key in seen:
                continue
            seen.add(key)
            targets.append(FrTarget(title_number=title_number, part_number=part_number))

    return targets
