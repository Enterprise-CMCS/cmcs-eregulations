"""Normalize raw eCFR structure trees into the eRegs upload structure contract."""

import html
from typing import Any

from .errors import EcfrTransformError
from .identifiers import identifier_tokens


def normalize_structure_for_upload(structure: dict[str, Any]) -> dict[str, Any]:
    """Normalize raw eCFR structure to the shape expected by eRegs uploads."""

    if not isinstance(structure, dict):
        raise EcfrTransformError("eCFR structure payload must be a JSON object")

    normalized = _normalize_node(structure, parent=[], parent_type="")
    return normalized


def _normalize_node(node: dict[str, Any], parent: list[str], parent_type: str) -> dict[str, Any]:
    """Recursively normalize one structure node and annotate parent metadata."""

    identifier = identifier_tokens(node.get("identifier"))
    node_type = _normalize_type(node.get("type"))
    children_raw = node.get("children")
    children: list[dict[str, Any]] = []
    if isinstance(children_raw, list):
        for child in children_raw:
            if isinstance(child, dict):
                children.append(_normalize_node(child, parent=identifier, parent_type=node_type))

    return {
        "identifier": identifier,
        "label": _safe_html_string(node.get("label")),
        "label_level": _safe_string(node.get("label_level")),
        "label_description": _safe_string(node.get("label_description")),
        "reserved": _normalize_reserved(node.get("reserved", False)),
        "type": node_type,
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


def _normalize_type(value: Any) -> str:
    """Normalize structure node type values to lowercase string tokens."""

    if not isinstance(value, str):
        return ""
    return value.strip().lower()


def _normalize_reserved(value: Any) -> bool:
    """Normalize reserved flags from booleans and common string/int forms."""

    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        return value != 0

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y"}:
            return True
        if normalized in {"false", "0", "no", "n", ""}:
            return False

    return False
