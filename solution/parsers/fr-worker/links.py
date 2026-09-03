"""Build FR section/range link payloads from extracted tokens.

This is a faithful Python port of the old Go FR parser's eregs.CreateSections
and eregs.CreateSectionRanges. A SECTNO token like "400.1" splits into a part
("400") and a section id ("1"); the part maps to a CFR title via the part =>
title map produced by the full-text XML scan.

The Go structs stored these as strings, but the eRegs
SectionCreateSerializer/SectionRangeCreateSerializer expect integer section
ids, so each builder converts section numbers to int for upload.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LinkSection:
    """An eRegs section location for one FR document."""

    title: str
    part: str
    section_id: int


@dataclass(frozen=True)
class LinkSectionRange:
    """An eRegs contiguous section range for one FR document."""

    title: str
    part: str
    first_sec: int
    last_sec: int


def create_sections(sections: list[str], part_map: dict[str, str]) -> list[LinkSection]:
    """Convert SECTNO tokens into LinkSection payloads keyed on the part map."""

    result: list[LinkSection] = []
    for section_token in sections:
        split = section_token.split(".")
        if len(split) != 2 or split[0] == "" or split[1] == "":
            logger.warning("[links] Section identifier %s is invalid.", section_token)
            continue

        part = split[0]
        title = part_map.get(part)
        if title is None:
            logger.warning("[links] Section identifier %s has no matching title.", section_token)
            continue

        section_id = _to_int(split[1], section_token)
        if section_id is None:
            continue

        result.append(LinkSection(title=title, part=part, section_id=section_id))
    return result


def create_section_ranges(ranges: list[str], part_map: dict[str, str]) -> list[LinkSectionRange]:
    """Convert section range tokens into LinkSectionRange payloads with part sharing."""

    result: list[LinkSectionRange] = []
    for range_token in ranges:
        split_sections = range_token.split("-")
        if len(split_sections) != 2 or split_sections[0] == "" or split_sections[1] == "":
            logger.warning("[links] section range %s is invalid", range_token)
            continue

        resolved = create_sections(split_sections, part_map)
        if len(resolved) != 2:
            logger.warning("[links] section range %s is invalid", range_token)
            continue

        if resolved[0].part != resolved[1].part:
            logger.warning("[links] Section identifier %s contains different parts.", range_token)
            continue

        result.append(
            LinkSectionRange(
                title=resolved[0].title,
                part=resolved[0].part,
                first_sec=resolved[0].section_id,
                last_sec=resolved[1].section_id,
            )
        )
    return result


def _to_int(value: str, token: str) -> int | None:
    """Coerce a section token tail to int, returning None on parse failure."""

    try:
        return int(value)
    except ValueError:
        logger.warning("[links] Section identifier %s is invalid.", token)
        return None
