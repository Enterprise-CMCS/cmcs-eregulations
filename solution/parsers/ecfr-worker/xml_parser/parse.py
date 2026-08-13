"""Entry points and parsing stubs for transforming eCFR part XML to document JSON."""

from typing import Any
from xml.etree import ElementTree

from .errors import EcfrXmlParseError
from .models import PartNode
from .normalize import normalize_part_for_eregs
from .postprocess import postprocess_part_node


def parse_part_xml_to_document(raw_xml: str, *, title_number: int, part_number: int) -> dict[str, Any]:
    """Parse raw eCFR part XML into eRegs-compatible document JSON.

    This is intentionally a skeleton seam so parse details can be filled in
    incrementally while the worker integration remains stable.
    """

    root = _parse_xml_root(raw_xml)
    part = _parse_part_root(root, title_number=title_number, part_number=part_number)
    part = postprocess_part_node(part)
    return normalize_part_for_eregs(part)


def _parse_xml_root(raw_xml: str) -> ElementTree.Element:
    """Parse XML text into root element, raising typed parser errors."""

    if not isinstance(raw_xml, str) or not raw_xml.strip():
        raise EcfrXmlParseError("eCFR XML payload must be a non-empty string")

    try:
        return ElementTree.fromstring(raw_xml)
    except ElementTree.ParseError as exc:
        raise EcfrXmlParseError(f"unable to parse eCFR XML payload: {exc}") from exc


def _parse_part_root(root: ElementTree.Element, *, title_number: int, part_number: int) -> PartNode:
    """Build a PartNode from the XML root element.

    This maps the top-level DIV5 part payload into the intermediate model and
    captures root metadata nodes (HEAD/AUTH/SOURCE/EDNOTE) expected by eRegs.
    """

    if root.tag != "DIV5":
        raise EcfrXmlParseError(f"expected part root tag DIV5, found {root.tag}")

    node_type = (root.attrib.get("TYPE") or "").strip().upper()
    if node_type and node_type != "PART":
        raise EcfrXmlParseError(f"expected part TYPE=PART, found TYPE={node_type}")

    part = PartNode(
        title_number=title_number,
        part_number=part_number,
        node_type="part",
        label=_parse_label_tokens(root.attrib.get("N", "")),
        title=_read_child_text(root, "HEAD"),
        authority=_parse_metadata_node(root, "AUTH", node_type="authority"),
        source=_parse_metadata_node(root, "SOURCE", node_type="source"),
        editorial_note=_parse_metadata_node(root, "EDNOTE", node_type="editorial_note"),
        children=_parse_part_children(root),
    )
    return part


def _parse_metadata_node(root: ElementTree.Element, tag: str, *, node_type: str) -> dict[str, str] | None:
    """Parse AUTH/SOURCE/EDNOTE style nodes into a normalized dict shape."""

    node = root.find(tag)
    if node is None:
        return None

    return {
        "node_type": node_type,
        "header": _read_child_text(node, "HED"),
        "content": _read_child_text(node, "PSPACE"),
    }


def _parse_part_children(root: ElementTree.Element) -> list[dict[str, Any]]:
    """Parse top-level part children using tag-based dispatch.

    This mirrors the legacy parser's high-level part contract where DIV6 nodes
    are subparts, DIV8 nodes are sections, and DIV9 nodes are appendices.
    """

    children: list[dict[str, Any]] = []
    for child in root:
        if child.tag == "DIV6":
            children.append(_parse_subpart(child))
            continue
        if child.tag == "DIV8":
            children.append(_parse_section(child))
            continue
        if child.tag == "DIV9":
            children.append(_parse_appendix(child))
            continue

        # Unknown part-level tags are skipped to match legacy permissive behavior.
        continue

    return children


def _parse_subpart(node: ElementTree.Element) -> dict[str, Any]:
    """Parse a DIV6 subpart node and its supported children."""

    children: list[dict[str, Any]] = []
    for child in node:
        if child.tag == "HEAD":
            continue
        if child.tag == "DIV8":
            children.append(_parse_section(child))
            continue
        if child.tag == "DIV7":
            children.append(_parse_subject_group(child))
            continue
        if child.tag == "DIV9":
            children.append(_parse_appendix(child))
            continue
        if child.tag == "SOURCE":
            parsed_source = _parse_metadata_node(node, "SOURCE", node_type="source")
            if parsed_source is not None:
                children.append(parsed_source)
            continue

    return {
        "node_type": "subpart",
        "label": _parse_label_tokens(node.attrib.get("N", "")),
        "title": _read_child_text(node, "HEAD"),
        "children": children,
    }


def _parse_subject_group(node: ElementTree.Element) -> dict[str, Any]:
    """Parse a DIV7 subject group with section/footnote children."""

    children: list[dict[str, Any]] = []
    for child in node:
        if child.tag == "HEAD":
            continue
        if child.tag == "DIV8":
            children.append(_parse_section(child))
            continue
        if child.tag == "FTNT":
            children.append({"node_type": "footnote", "content": _collect_inner_xml(child)})
            continue

    return {
        "node_type": "subject_group",
        "label": _parse_label_tokens(node.attrib.get("N", "")),
        "title": _read_child_text(node, "HEAD"),
        "children": children,
    }


def _parse_section(node: ElementTree.Element) -> dict[str, Any]:
    """Parse a DIV8 section with supported child content nodes."""

    children: list[dict[str, Any]] = []
    for child in node:
        if child.tag == "HEAD":
            continue
        children.append(_parse_section_child(child))

    return {
        "node_type": "section",
        "label": _parse_label_tokens(node.attrib.get("N", "")),
        "title": _read_child_text(node, "HEAD"),
        "children": [c for c in children if c is not None],
    }


def _parse_appendix(node: ElementTree.Element) -> dict[str, Any]:
    """Parse a DIV9 appendix and supported paragraph/heading style children."""

    children: list[dict[str, Any]] = []
    for child in node:
        if child.tag == "HEAD":
            continue
        parsed = _parse_appendix_child(child)
        if parsed is not None:
            children.append(parsed)

    return {
        "node_type": "appendix",
        "label": _parse_appendix_label_tokens(node.attrib.get("N", "")),
        "title": _read_child_text(node, "HEAD"),
        "children": children,
    }


def _parse_section_child(node: ElementTree.Element) -> dict[str, Any] | None:
    """Parse supported section child tags into normalized node dicts."""

    if node.tag == "P":
        return {"node_type": "paragraph", "text": _collect_inner_xml(node)}
    if node.tag in {"FP", "FP-1", "FP-2"}:
        return {"node_type": "flush_paragraph", "text": _collect_inner_xml(node)}
    if node.tag == "img":
        return {"node_type": "image", "src": (node.attrib.get("src") or "").strip()}
    if node.tag == "EXTRACT":
        return {"node_type": "extract", "content": _collect_inner_xml(node)}
    if node.tag == "CITA":
        return {"node_type": "citation", "content": _collect_inner_xml(node)}
    if node.tag == "SECAUTH":
        return {"node_type": "section_authority", "content": _collect_inner_xml(node)}
    if node.tag == "FTNT":
        return {"node_type": "footnote", "content": _collect_inner_xml(node)}
    if node.tag == "DIV":
        return {"node_type": "division", "content": _collect_inner_xml(node)}
    if node.tag == "EFFDNOT":
        return {
            "node_type": "effective_date_note",
            "header": _read_child_text(node, "HED"),
            "content": _read_child_text(node, "PSPACE"),
        }
    return None


def _parse_appendix_child(node: ElementTree.Element) -> dict[str, Any] | None:
    """Parse supported appendix child tags into normalized node dicts."""

    if node.tag == "P":
        return {"node_type": "paragraph", "text": _collect_inner_xml(node)}
    if node.tag in {"FP", "FP-1", "FP-2"}:
        return {"node_type": "flush_paragraph", "text": _collect_inner_xml(node)}
    if node.tag in {"HD1", "HD2", "HD3"}:
        return {"node_type": "heading", "level": node.tag, "content": _collect_inner_xml(node)}
    if node.tag == "DIV":
        return {"node_type": "division", "content": _collect_inner_xml(node)}
    if node.tag == "TABLE":
        return {"node_type": "table", "content": _collect_inner_xml(node)}
    if node.tag == "FTNT":
        return {"node_type": "footnote", "content": _collect_inner_xml(node)}
    if node.tag == "CITA":
        return {"node_type": "citation", "content": _collect_inner_xml(node)}
    return None


def _parse_label_tokens(value: str) -> list[str]:
    """Split legacy N-attribute labels into token arrays."""

    if not value:
        return []
    tokens: list[str] = []
    for section in value.split("-"):
        for token in section.split("."):
            token = token.strip()
            if token:
                tokens.append(token)
    return tokens


def _parse_appendix_label_tokens(value: str) -> list[str]:
    """Split appendix-style N labels by whitespace tokens."""

    if not value:
        return []
    return [token for token in value.split(" ") if token]


def _read_child_text(root: ElementTree.Element, tag: str) -> str:
    """Read direct child text by tag, defaulting to empty string."""

    child = root.find(tag)
    if child is None:
        return ""
    return _collect_inner_text(child)


def _collect_inner_text(node: ElementTree.Element) -> str:
    """Collect concatenated inner text for a node."""

    return "".join(node.itertext()).strip()


def _collect_inner_xml(node: ElementTree.Element) -> str:
    """Collect inner XML (not flattened text) for rich-content nodes."""

    parts: list[str] = []
    if node.text:
        parts.append(node.text)

    for child in list(node):
        parts.append(ElementTree.tostring(child, encoding="unicode"))

    return "".join(parts).strip()
