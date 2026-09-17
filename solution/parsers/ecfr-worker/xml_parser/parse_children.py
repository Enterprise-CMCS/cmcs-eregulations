"""Parsers for section and appendix child node content."""

from typing import Any
from xml.etree import ElementTree

from .readers import collect_inner_xml, read_child_text
from .splitters import split_paragraph_node


def parse_section_child(node: ElementTree.Element) -> dict[str, Any] | list[dict[str, Any]] | None:
    """Parse supported section child tags into normalized node dicts."""

    if node.tag == "P":
        return split_paragraph_node(collect_inner_xml(node))
    if node.tag in {"FP", "FP-1", "FP-2"}:
        return {"node_type": "FlushParagraph", "text": collect_inner_xml(node)}
    if node.tag == "img":
        return {"node_type": "Image", "src": (node.attrib.get("src") or "").strip()}
    if node.tag == "EXTRACT":
        return {"node_type": "Extract", "content": collect_inner_xml(node)}
    if node.tag == "CITA":
        return {"node_type": "Citation", "content": collect_inner_xml(node)}
    if node.tag == "SECAUTH":
        return {"node_type": "SectionAuthority", "content": collect_inner_xml(node)}
    if node.tag == "FTNT":
        return {"node_type": "FootNote", "content": collect_inner_xml(node)}
    if node.tag == "DIV":
        return {"node_type": "Division", "content": collect_inner_xml(node)}
    if node.tag == "EFFDNOT":
        return {
            "node_type": "EffectiveDateNote",
            "header": read_child_text(node, "HED"),
            "content": read_child_text(node, "PSPACE"),
        }
    return None


def parse_appendix_child(node: ElementTree.Element) -> dict[str, Any] | None:
    """Parse supported appendix child tags into normalized node dicts."""

    if node.tag == "P":
        return {"node_type": "Paragraph", "text": collect_inner_xml(node)}
    if node.tag in {"FP", "FP-1", "FP-2"}:
        return {"node_type": "FlushParagraph", "text": collect_inner_xml(node)}
    if node.tag in {"HD1", "HD2", "HD3"}:
        heading_type = {"HD1": "Heading", "HD2": "Heading2", "HD3": "Heading3"}[node.tag]
        return {"node_type": heading_type, "content": collect_inner_xml(node)}
    if node.tag == "DIV":
        return {"node_type": "Division", "content": collect_inner_xml(node)}
    if node.tag == "TABLE":
        return {"node_type": "Table", "content": collect_inner_xml(node)}
    if node.tag == "FTNT":
        return {"node_type": "FootNote", "content": collect_inner_xml(node)}
    if node.tag == "CITA":
        return {"node_type": "Citation", "content": collect_inner_xml(node)}
    return None
