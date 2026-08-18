"""Post-processing hooks for parsed XML node trees.

This module ports key legacy parsexml post-processing behavior for paragraph
markers/citations so parsed document nodes more closely match eRegs contracts.
"""

import hashlib
import logging
import re
from typing import Any

from .models import PartNode

logger = logging.getLogger(__name__)

_MARKER_RE = re.compile(
    r"^\(([^\)]+)\)(?:(?: ?<I>[^<]+</I>(?: ?-)?)? ?\(([^\)]{1,3})\))?"
    r"(?: ?(?:<I>[^<]+</I>(?: ?-)?)? ?\(([^\)]{1,3})\))?"
)

_ALPHA_RE = re.compile(r"^[a-z]$")
_NUM_RE = re.compile(r"^\d+$")
_ROMAN_RE = re.compile(r"^(x|ix|iv|v|vi{1,3}|i{1,3})$")
_UPPER_RE = re.compile(r"^[A-Z]$")
_ITALIC_NUM_RE = re.compile(r"^<I>\d+</I>$")
_ITALIC_ROMAN_RE = re.compile(r"^<I>(ix|iv|v|vi{1,3}|i{1,3})</I>$")

_PARAGRAPH_HIERARCHY: list[re.Pattern[str]] = [
    _ALPHA_RE,
    _NUM_RE,
    _ROMAN_RE,
    _UPPER_RE,
    _ITALIC_NUM_RE,
    _ITALIC_ROMAN_RE,
]


def postprocess_part_node(part: PartNode) -> PartNode:
    """Apply post-processing pipeline to a parsed part model.

    Future implementation should mirror legacy parsexml post-processing steps.
    """

    _apply_paragraph_markers(part)
    _apply_paragraph_citations(part)
    _rewrite_embedded_image_sources(part)
    return part


def _apply_paragraph_citations(part: PartNode) -> None:
    """Generate section-scoped paragraph citation labels.

    Each section paragraph receives a full label containing the section label
    prefix plus the computed paragraph label; if no stable paragraph label can
    be computed, a deterministic md5 hash token is used.
    """

    for section in _iter_sections(part.children):
        section_label = section.get("label")
        if not isinstance(section_label, list):
            continue

        prev_label: list[str] | None = None
        for child in section.get("children", []):
            if not isinstance(child, dict) or child.get("node_type") != "Paragraph":
                continue

            marker = child.get("marker")
            if not isinstance(marker, list):
                marker = []

            local_label, citation_error = _generate_paragraph_citation(marker, prev_label)
            if local_label:
                child["label"] = [*section_label, *local_label]
            else:
                child["label"] = [*section_label, _paragraph_hash(child.get("text", ""))]

            if citation_error is not None:
                logger.warning(
                    "Error generating paragraph citation for prev=%s marker=%s: %s",
                    prev_label,
                    marker,
                    citation_error,
                )
                continue

            prev_label = local_label


def _apply_paragraph_markers(part: PartNode) -> None:
    """Extract paragraph markers from leading paragraph text markup."""

    for section in _iter_sections(part.children):
        for child in section.get("children", []):
            if not isinstance(child, dict) or child.get("node_type") != "Paragraph":
                continue
            marker = _extract_marker(child.get("text", ""))
            if marker:
                child["marker"] = marker


def _rewrite_embedded_image_sources(part: PartNode) -> None:
    """Rewrite legacy /graphics image sources to FR CDN large PNG URLs."""

    for image in _iter_image_nodes(part.children):
        src = image.get("src")
        if not isinstance(src, str):
            continue
        rewritten = _rewrite_graphics_source(src)
        if rewritten is not None:
            image["src"] = rewritten


def _iter_sections(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collect all section nodes from parsed part descendants."""

    out: list[dict[str, Any]] = []

    def walk(node_list: list[dict[str, Any]]) -> None:
        for node in node_list:
            if not isinstance(node, dict):
                continue
            if node.get("node_type") == "SECTION":
                out.append(node)
            children = node.get("children")
            if isinstance(children, list):
                walk(children)

    walk(nodes)
    return out


def _iter_image_nodes(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collect all image nodes from parsed part descendants."""

    out: list[dict[str, Any]] = []

    def walk(node_list: list[dict[str, Any]]) -> None:
        for node in node_list:
            if not isinstance(node, dict):
                continue
            if node.get("node_type") == "Image":
                out.append(node)
            children = node.get("children")
            if isinstance(children, list):
                walk(children)

    walk(nodes)
    return out


def _rewrite_graphics_source(src: str) -> str | None:
    """Convert /graphics image src paths to canonical FR CDN PNG URLs."""

    if not src.startswith("/graphics/"):
        return None

    filename = src.split("/")[2] if len(src.split("/")) > 2 else ""
    parts = filename.split(".")
    if len(parts) < 2:
        return None

    if len(parts) > 2 and parts[-2].lower() == "eps":
        name_parts = parts[:-2]
    else:
        name_parts = parts[:-1]

    image_name = ".".join(name_parts).upper()
    return f"https://images.federalregister.gov/{image_name}/large.png"


def _extract_marker(text: Any) -> list[str] | None:
    """Extract up to three leading marker tokens from paragraph content."""

    if not isinstance(text, str):
        return None

    match = _MARKER_RE.search(text)
    if match is None:
        return None

    labels = [group for group in match.groups() if group]
    return labels or None


def _match_label_type(label: str) -> int:
    """Map one marker token to hierarchy level (or -1 when unknown)."""

    level = -1
    for idx, matcher in enumerate(_PARAGRAPH_HIERARCHY):
        if matcher.search(label):
            level = idx
    return level


def _paragraph_level(label: list[str] | None, marker: list[str] | None) -> int:
    """Return hierarchical level for a paragraph based on label/marker."""

    if label:
        return len(label) - 1
    if not marker:
        return -1
    return _match_label_type(marker[-1])


def _generate_paragraph_citation(marker: list[str], prev_label: list[str] | None) -> tuple[list[str], str | None]:
    """Generate local paragraph citation tokens with optional ordering error details."""

    if not marker:
        return [], None

    current_level = _match_label_type(marker[0])
    if current_level == 0:
        return marker, None

    if not prev_label:
        return [], None

    prev_level = _paragraph_level(prev_label, None)

    if current_level == 2:
        if len(marker) > 1 and _match_label_type(marker[1]) == 1:
            return marker, None
        if marker[0] == "i" and prev_level != 1:
            return marker, None
        if marker[0] == "v" and (len(prev_label) < 3 or prev_label[2] != "iv"):
            return marker, None

    if prev_level - current_level < -1:
        return [], "this paragraph and its neighbor are not in the right order"

    cut = current_level
    if len(prev_label) < current_level:
        if current_level - 1 != len(prev_label):
            return [], "this paragraph and its neighbor are not in the right order"
        cut -= 1

    return [*prev_label[:cut], *marker], None


def _paragraph_hash(text: Any) -> str:
    """Return deterministic md5 hash token for unlabeled paragraph text."""

    if not isinstance(text, str):
        text = ""
    return hashlib.md5(text.encode("utf-8")).hexdigest()
