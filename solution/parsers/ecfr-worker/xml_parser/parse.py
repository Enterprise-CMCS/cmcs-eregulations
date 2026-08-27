"""Entry point for eCFR XML parser modules."""

from typing import Any
from xml.etree import ElementTree

from .errors import EcfrXmlParseError
from .labels import parse_label_tokens, resolve_div_node_type
from .metadata import parse_metadata_node
from .models import PartNode
from .normalize import normalize_part_for_eregs
from .parse_divs import (
    parse_appendix,
    parse_part_children,
    parse_section,
    parse_subject_group,
    parse_subpart,
)
from .postprocess import postprocess_part_node
from .readers import read_child_text


def parse_part_xml_to_document(raw_xml: str, *, title_number: int, part_number: int) -> dict[str, Any]:
    """Parse raw eCFR part XML into eRegs-compatible document JSON."""

    root = _parse_xml_root(raw_xml)
    part = parse_part_root(root, title_number=title_number, part_number=part_number)
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


def parse_part_root(root: ElementTree.Element, *, title_number: int, part_number: int) -> PartNode:
    """Build a PartNode from the XML root element."""

    if root.tag != "DIV5":
        raise EcfrXmlParseError(f"expected part root tag DIV5, found {root.tag}")

    node_type = resolve_div_node_type(root)
    if node_type and node_type != "PART":
        raise EcfrXmlParseError(f"expected part TYPE=PART, found TYPE={node_type}")

    return PartNode(
        title_number=title_number,
        part_number=part_number,
        node_type=node_type,
        label=parse_label_tokens(root.attrib.get("N", "")),
        title=read_child_text(root, "HEAD"),
        authority=parse_metadata_node(root, "AUTH", node_type="Authority"),
        source=parse_metadata_node(root, "SOURCE", node_type="Source"),
        editorial_note=parse_metadata_node(root, "EDNOTE", node_type="EdNote"),
        children=parse_part_children(root),
    )
