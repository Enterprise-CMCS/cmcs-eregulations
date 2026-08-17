"""XML child-reading helpers for eCFR parser nodes."""

from xml.etree import ElementTree


def read_child_text(root: ElementTree.Element, tag: str) -> str:
    """Read direct child text by tag, defaulting to empty string."""

    child = root.find(tag)
    if child is None:
        return ""
    return collect_inner_text(child)


def read_child_inner_xml(root: ElementTree.Element, tag: str) -> str:
    """Read direct child inner XML by tag, defaulting to empty string."""

    child = root.find(tag)
    if child is None:
        return ""
    return collect_inner_xml(child)


def collect_inner_text(node: ElementTree.Element) -> str:
    """Collect concatenated inner text for a node."""

    return "".join(node.itertext()).strip()


def collect_inner_xml(node: ElementTree.Element) -> str:
    """Collect inner XML (not flattened text) for rich-content nodes."""

    parts: list[str] = []
    if node.text:
        parts.append(node.text)

    for child in list(node):
        parts.append(ElementTree.tostring(child, encoding="unicode"))

    return "".join(parts).strip()
