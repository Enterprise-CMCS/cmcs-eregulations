"""Parsers for DIV-based part/subpart/section/appendix structures."""

from typing import Any
from xml.etree import ElementTree

from .labels import parse_appendix_label_tokens, parse_label_tokens, resolve_div_node_type
from .metadata import parse_metadata_element
from .parse_children import parse_appendix_child, parse_section_child
from .readers import collect_inner_xml, read_child_inner_xml, read_child_text


def parse_part_children(root: ElementTree.Element) -> list[dict[str, Any]]:
    """Parse top-level part children using tag-based dispatch."""

    children: list[dict[str, Any]] = []
    for child in root:
        if child.tag == "HEAD":
            continue
        if child.tag == "DIV6":
            children.append(parse_subpart(child))
            continue
        if child.tag == "DIV8":
            children.append(parse_section(child))
            continue
        if child.tag == "DIV9":
            children.append(parse_appendix(child))
            continue

    return children


def parse_subpart(node: ElementTree.Element) -> dict[str, Any]:
    """Parse a DIV6 subpart node and its supported children."""

    children: list[dict[str, Any]] = []
    for child in node:
        if child.tag == "HEAD":
            continue
        if child.tag == "DIV8":
            children.append(parse_section(child))
            continue
        if child.tag == "DIV7":
            children.append(parse_subject_group(child))
            continue
        if child.tag == "DIV9":
            children.append(parse_appendix(child))
            continue
        if child.tag == "SOURCE":
            children.append(parse_metadata_element(child, node_type="Source"))
            continue

    return {
        "node_type": resolve_div_node_type(node),
        "label": parse_label_tokens(node.attrib.get("N", "")),
        "title": read_child_text(node, "HEAD"),
        "children": children,
    }


def parse_subject_group(node: ElementTree.Element) -> dict[str, Any]:
    """Parse a DIV7 subject group with section/footnote children."""

    children: list[dict[str, Any]] = []
    for child in node:
        if child.tag == "HEAD":
            continue
        if child.tag == "DIV8":
            children.append(parse_section(child))
            continue
        if child.tag == "FTNT":
            children.append({"node_type": "FootNote", "content": collect_inner_xml(child)})
            continue

    return {
        "node_type": resolve_div_node_type(node),
        "label": parse_label_tokens(node.attrib.get("N", "")),
        "title": read_child_inner_xml(node, "HEAD"),
        "children": children,
    }


def parse_section(node: ElementTree.Element) -> dict[str, Any]:
    """Parse a DIV8 section with supported child content nodes."""

    children: list[dict[str, Any]] = []
    for child in node:
        if child.tag == "HEAD":
            continue
        parsed = parse_section_child(child)
        if parsed is None:
            continue
        if isinstance(parsed, list):
            children.extend(parsed)
        else:
            children.append(parsed)

    return {
        "node_type": resolve_div_node_type(node),
        "label": parse_label_tokens(node.attrib.get("N", "")),
        "title": read_child_text(node, "HEAD"),
        "children": [c for c in children if c is not None],
    }


def parse_appendix(node: ElementTree.Element) -> dict[str, Any]:
    """Parse a DIV9 appendix and supported paragraph/heading style children."""

    children: list[dict[str, Any]] = []
    for child in node:
        if child.tag == "HEAD":
            continue
        parsed = parse_appendix_child(child)
        if parsed is not None:
            children.append(parsed)

    return {
        "node_type": resolve_div_node_type(node),
        "label": parse_appendix_label_tokens(node.attrib.get("N", "")),
        "title": read_child_text(node, "HEAD"),
        "children": children,
    }
