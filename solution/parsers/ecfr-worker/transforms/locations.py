"""Location extraction helpers for part depth, sections, and subparts."""

from typing import Any

from .errors import EcfrTransformError
from .identifiers import first_identifier_token, parse_section_identifier


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
    title_str = first_identifier_token(structure.get("identifier"))
    if title_str is None:
        raise EcfrTransformError("unable to determine title identifier from eCFR structure")

    part_str = first_identifier_token(part_node.get("identifier")) or part_number_str
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

    subpart_id = first_identifier_token(subpart_node.get("identifier")) or ""
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

    part_str, section_str = parse_section_identifier(node.get("identifier"), fallback_part_str)
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
        identifier = first_identifier_token(node.get("identifier"))
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
