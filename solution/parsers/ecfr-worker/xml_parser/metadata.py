"""Metadata node parsers for AUTH/SOURCE/EDNOTE elements."""

from xml.etree import ElementTree

from .readers import read_child_text


def parse_metadata_node(root: ElementTree.Element, tag: str, *, node_type: str) -> dict[str, str] | None:
    """Parse AUTH/SOURCE/EDNOTE style nodes into a normalized dict shape."""

    node = root.find(tag)
    if node is None:
        return None

    return parse_metadata_element(node, node_type=node_type)


def parse_metadata_element(node: ElementTree.Element, *, node_type: str) -> dict[str, str]:
    """Parse a metadata element node (AUTH/SOURCE/EDNOTE) into dict shape."""

    return {
        "node_type": node_type,
        "header": read_child_text(node, "HED"),
        "content": read_child_text(node, "PSPACE"),
    }
