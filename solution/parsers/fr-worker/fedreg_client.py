"""Federal Register full-text XML section/CFR extraction for the FR worker.

This is a faithful Python port of the old Go FR parser's fedreg.FetchSections
(and its extractSection/extractCFR helpers). It parses a document's
full-text XML, collecting SECTNO section identifiers (and section ranges) while
building a part => title map from CFR references that fall within the
configured title set.
"""

import logging
import re
import xml.etree.ElementTree as ET

import requests
from common.http import execute_request

logger = logging.getLogger(__name__)

_SECTION_RANGE_RE = re.compile(r"\d+\.\d+-\d+\.\d+")
_SECTION_RE = re.compile(r"\d+\.\d+")
_DIGIT_RE = re.compile(r"\d+")


class FedRegClientError(RuntimeError):
    """Raised for failed or malformed Federal Register full-text responses."""

    pass


def fetch_full_text_sections(
    full_text_xml_url: str,
    titles: set[str],
    timeout: int = 60,
) -> tuple[list[str], list[str], dict[str, str]]:
    """Extract sections, section ranges, and a part => title map from FR XML.

    Returns (sections, ranges, part_map) mirroring the old fedreg.FetchSections:
      - sections: individual SECTNO tokens, e.g. "400.1"
      - ranges:   section range tokens, e.g. "400.1-400.5"
      - part_map: {part: title} drawn only from CFR references whose title is
        in the configured title set.
    """

    response = execute_request(
        lambda: requests.get(full_text_xml_url, timeout=timeout),
        on_http_error=lambda exc: FedRegClientError(
            f"Federal Register full text request failed "
            f"({exc.response.status_code if exc.response is not None else 'unknown'})"
        ),
        on_request_error=lambda exc: FedRegClientError(f"Federal Register full text request failed: {exc}"),
    )

    part_map: dict[str, str] = {}
    sections: list[str] = []
    ranges: list[str] = []

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as exc:
        raise FedRegClientError("Federal Register full text XML could not be parsed") from exc

    for element in root.iter():
        tag = element.tag.rsplit("}", 1)[-1]
        if tag not in ("SECTNO", "CFR"):
            continue
        text = "".join(element.itertext()).strip()

        if tag == "CFR":
            try:
                title, parts = _extract_cfr(text)
            except ValueError as exc:
                logger.warning("[fedreg] failed to extract CFR information from %r: %s", text, exc)
                continue
            if title in titles:
                for part in parts:
                    part_map.setdefault(part, title)
        elif tag == "SECTNO":
            try:
                section, section_range = _extract_section(text)
            except ValueError as exc:
                logger.warning("[fedreg] %s", exc)
                continue
            if section_range:
                ranges.append(section_range)
            elif section:
                sections.append(section)

    return sections, ranges, part_map


def _extract_section(input_text: str) -> tuple[str, str]:
    """Port of fedreg.extractSection: return (section, range) or (section, '')."""

    range_match = _SECTION_RANGE_RE.findall(input_text)
    if range_match:
        return "", range_match[0]
    section_match = _SECTION_RE.findall(input_text)
    if not section_match:
        raise ValueError(f"failed to extract section from {input_text}")
    return section_match[0], ""


def _extract_cfr(input_text: str) -> tuple[str, list[str]]:
    """Port of fedreg.extractCFR: return (title, parts) from a CFR reference."""

    split = input_text.split(" ")
    if len(split) < 1:
        raise ValueError("the CFR string is empty")

    title = split[0]
    if not _DIGIT_RE.search(title):
        raise ValueError(f"title '{title}' is not a valid title")

    parts: list[str] = []
    for token in split[1:]:
        part = token.strip().strip(".,;:")
        if _DIGIT_RE.search(part):
            parts.append(part)

    if len(parts) < 1:
        raise ValueError("parts list is empty")

    return title, parts
