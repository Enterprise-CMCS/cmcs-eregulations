"""Structure transformation helpers for eCFR location metadata.

These helpers convert raw eCFR structure payloads into the depth/sections/
subparts shape expected by the eRegs part upload endpoint.
"""

import html
from typing import Any


class EcfrTransformError(RuntimeError):
    """Raised when required structure nodes cannot be located or parsed."""

    pass


def normalize_structure_for_upload(structure: dict[str, Any]) -> dict[str, Any]:
    """Normalize raw eCFR structure to the shape expected by eRegs uploads."""

    if not isinstance(structure, dict):
        raise EcfrTransformError("eCFR structure payload must be a JSON object")

    normalized = _normalize_node(structure, parent=[], parent_type="")
    return normalized


def determine_part_depth(structure: dict[str, Any], part_number: int) -> int:
    """Return nesting depth of the requested part within title structure."""

    part_number_str = str(part_number)
    result = _find_part_node(structure, part_number_str)
    if result is None:
        raise EcfrTransformError(f"unable to locate part {part_number_str} in eCFR structure")
    _part_node, depth = result
    return depth


def extract_sections_and_subparts(
    structure: dict[str, Any],
    part_number: int,
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    """Extract non-reserved sections/subparts for one requested part node."""

    part_number_str = str(part_number)
    result = _find_part_node(structure, part_number_str)
    if result is None:
        raise EcfrTransformError(f"unable to locate part {part_number_str} in eCFR structure")

    part_node, _depth = result
    title_str = _first_identifier_token(structure.get("identifier"))
    if title_str is None:
        raise EcfrTransformError("unable to determine title identifier from eCFR structure")

    part_str = _first_identifier_token(part_node.get("identifier")) or part_number_str
    sections: list[dict[str, str]] = []
    subparts: list[dict[str, Any]] = []

    children = part_node.get("children")
    if not isinstance(children, list):
        return sections, subparts

    for child in children:
        if not isinstance(child, dict):
            continue
        if child.get("reserved") is True:
            continue

        child_type = child.get("type")
        if child_type == "section":
            section = _build_section(title_str, part_str, child)
            if section is not None:
                sections.append(section)
        elif child_type == "subpart":
            subparts.append(_build_subpart(title_str, part_str, child))

    return sections, subparts


def _build_subpart(title_str: str, part_str: str, subpart_node: dict[str, Any]) -> dict[str, Any]:
    """Build normalized subpart payload with nested section entries."""

    subpart_id = _first_identifier_token(subpart_node.get("identifier")) or ""
    subpart_sections: list[dict[str, str]] = []

    children = subpart_node.get("children")
    if isinstance(children, list):
        for child in children:
            if not isinstance(child, dict) or child.get("reserved") is True:
                continue

            child_type = child.get("type")
            if child_type == "section":
                section = _build_section(title_str, part_str, child)
                if section is not None:
                    subpart_sections.append(section)
            elif child_type == "subject_group":
                nested = child.get("children")
                if not isinstance(nested, list):
                    continue
                for nested_child in nested:
                    if not isinstance(nested_child, dict):
                        continue
                    if nested_child.get("type") != "section" or nested_child.get("reserved") is True:
                        continue
                    section = _build_section(title_str, part_str, nested_child)
                    if section is not None:
                        subpart_sections.append(section)

    return {
        "title": title_str,
        "part": part_str,
        "subpart": subpart_id,
        "sections": subpart_sections,
    }


def _build_section(title_str: str, fallback_part_str: str, node: dict[str, Any]) -> dict[str, str] | None:
    """Build normalized section location payload from structure node."""

    part_str, section_str = _parse_section_identifier(node.get("identifier"), fallback_part_str)
    if section_str is None:
        return None

    return {
        "title": title_str,
        "part": part_str,
        "section": section_str,
    }


def _find_part_node(node: Any, part_number_str: str, depth: int = 0) -> tuple[dict[str, Any], int] | None:
    """Depth-first search for a part node and its nesting depth."""

    if not isinstance(node, dict):
        return None

    if node.get("type") == "part":
        identifier = _first_identifier_token(node.get("identifier"))
        if identifier == part_number_str:
            return node, depth

    children = node.get("children")
    if not isinstance(children, list):
        return None

    for child in children:
        result = _find_part_node(child, part_number_str, depth + 1)
        if result is not None:
            return result

    return None


def _first_identifier_token(identifier: Any) -> str | None:
    """Return first identifier token from eCFR identifier values."""

    tokens = _identifier_tokens(identifier)
    if not tokens:
        return None
    return tokens[0]


def _parse_section_identifier(identifier: Any, fallback_part_str: str) -> tuple[str, str | None]:
    """Split eCFR section identifiers into part and section components."""

    tokens = _identifier_tokens(identifier)
    if not tokens:
        return fallback_part_str, None

    if len(tokens) == 1:
        value = tokens[0]
        if "." in value:
            first, rest = value.split(".", 1)
            if first and rest:
                return first, rest
        return fallback_part_str, value

    return tokens[0], ".".join(tokens[1:])


def _identifier_tokens(identifier: Any) -> list[str]:
    """Normalize identifier strings/lists into non-empty token lists."""

    if isinstance(identifier, str):
        value = identifier.strip()
        if not value:
            return []
        tokens: list[str] = []
        for piece in value.split("."):
            segment = piece.strip()
            if not segment:
                continue
            tokens.extend(token for token in segment.split(" ") if token)
        return tokens

    if isinstance(identifier, list):
        tokens: list[str] = []
        for item in identifier:
            if isinstance(item, str) and item.strip():
                tokens.append(item.strip())
        return tokens

    return []


def _normalize_node(node: dict[str, Any], parent: list[str], parent_type: str) -> dict[str, Any]:
    """Recursively normalize one structure node and annotate parent metadata."""

    identifier = _identifier_tokens(node.get("identifier"))
    children_raw = node.get("children")
    children: list[dict[str, Any]] = []
    if isinstance(children_raw, list):
        for child in children_raw:
            if isinstance(child, dict):
                children.append(_normalize_node(child, parent=identifier, parent_type=_safe_string(node.get("type"))))

    return {
        "identifier": identifier,
        "label": _safe_html_string(node.get("label")),
        "label_level": _safe_string(node.get("label_level")),
        "label_description": _safe_string(node.get("label_description")),
        "reserved": bool(node.get("reserved", False)),
        "type": _safe_string(node.get("type")),
        "children": children,
        "descendant_range": _normalize_descendant_range(node.get("descendant_range")),
        "parent_type": parent_type,
        "parent": parent,
    }


def _safe_string(value: Any) -> str:
    """Return string values as-is; coerce non-strings to empty string."""

    if isinstance(value, str):
        return value
    return ""


def _safe_html_string(value: Any) -> str:
    """Return HTML-unescaped string values; coerce non-strings to empty string."""

    if isinstance(value, str):
        return html.unescape(value)
    return ""


def _normalize_descendant_range(value: Any) -> list[str]:
    """Normalize descendant_range to a string list across eCFR payload variants."""

    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if isinstance(value, str):
        candidate = value.strip()
        if not candidate:
            return []

        if " – " in candidate:
            return [piece.strip() for piece in candidate.split(" – ") if piece.strip()]

        if " - " in candidate:
            return [piece.strip() for piece in candidate.split(" - ") if piece.strip()]

        return [candidate]

    return []
