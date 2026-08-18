"""Normalization from XML parser intermediate models to eRegs document payloads."""

from typing import Any

from .models import PartNode


_CONTAINER_NODE_TYPES = {"PART", "SUBPART", "SUBJGRP", "SECTION", "APPENDIX"}
_CONTENT_NODE_TYPES = {
    "Extract",
    "Citation",
    "SectionAuthority",
    "FootNote",
    "Division",
    "Heading",
    "Heading2",
    "Heading3",
    "Table",
}
_METADATA_NODE_TYPES = {"Source", "Authority", "EdNote"}


def normalize_part_for_eregs(part: PartNode) -> dict[str, Any]:
    """Convert parsed and post-processed part model into strict eRegs JSON."""

    return _normalize_part(part)


def _normalize_part(part: PartNode) -> dict[str, Any]:
    """Normalize the top-level PartNode into the canonical payload schema."""

    normalized = {
        "node_type": _as_string(part.node_type),
        "label": _as_string_list(part.label),
        "title": _as_string(part.title),
        "children": _normalize_children(part.children),
        "authority": _normalize_metadata_node(part.authority),
        "source": _normalize_metadata_node(part.source),
        "editorial_note": _normalize_metadata_node(part.editorial_note),
    }
    return normalized


def _normalize_children(children: Any) -> list[dict[str, Any]]:
    """Normalize child node arrays, dropping non-dict entries."""

    if not isinstance(children, list):
        return []

    out: list[dict[str, Any]] = []
    for child in children:
        if not isinstance(child, dict):
            continue
        out.append(_normalize_node(child))
    return out


def _normalize_metadata_node(node: Any) -> dict[str, Any] | None:
    """Normalize top-level metadata node fields or return None when absent."""

    if not isinstance(node, dict):
        return None
    normalized = _normalize_node(node)
    if normalized.get("node_type") in _METADATA_NODE_TYPES:
        return normalized
    return None


def _normalize_node(node: dict[str, Any]) -> dict[str, Any]:
    """Normalize one parsed node with strict per-type allowlists."""

    node_type = _as_string(node.get("node_type"))

    if node_type in _CONTAINER_NODE_TYPES:
        return {
            "node_type": node_type,
            "label": _as_string_list(node.get("label")),
            "title": _as_string(node.get("title")),
            "children": _normalize_children(node.get("children")),
        }

    if node_type == "Paragraph":
        return {
            "node_type": node_type,
            "text": _as_string(node.get("text")),
            "label": _as_string_list(node.get("label")),
            "marker": _as_string_list(node.get("marker")),
        }

    if node_type == "FlushParagraph":
        return {
            "node_type": node_type,
            "text": _as_string(node.get("text")),
        }

    if node_type == "Image":
        return {
            "node_type": node_type,
            "src": _as_string(node.get("src")),
        }

    if node_type in _CONTENT_NODE_TYPES:
        return {
            "node_type": node_type,
            "content": _as_string(node.get("content")),
        }

    if node_type == "EffectiveDateNote":
        return {
            "node_type": node_type,
            "header": _as_string(node.get("header")),
            "content": _as_string(node.get("content")),
        }

    if node_type in _METADATA_NODE_TYPES:
        return {
            "node_type": node_type,
            "header": _as_string(node.get("header")),
            "content": _as_string(node.get("content")),
        }

    return {
        "node_type": node_type,
        "children": _normalize_children(node.get("children")),
    }


def _as_string(value: Any) -> str:
    """Return value as a string when already string-like; otherwise empty."""

    if isinstance(value, str):
        return value
    return ""


def _as_string_list(value: Any) -> list[str]:
    """Normalize a value to a list of non-empty strings."""

    if not isinstance(value, list):
        return []

    out: list[str] = []
    for item in value:
        if isinstance(item, str) and item:
            out.append(item)
    return out
