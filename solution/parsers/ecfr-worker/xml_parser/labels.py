"""Label and node-type helpers for eCFR XML parsing."""

from xml.etree import ElementTree

_DIV_NODE_TYPE_FALLBACKS: dict[str, str] = {
    "DIV5": "PART",
    "DIV6": "SUBPART",
    "DIV7": "SUBJGRP",
    "DIV8": "SECTION",
    "DIV9": "APPENDIX",
}


def resolve_div_node_type(node: ElementTree.Element) -> str:
    """Resolve DIV node_type from TYPE attribute with fallback."""

    type_value = (node.attrib.get("TYPE") or "").strip().upper()
    if type_value:
        return type_value
    return _DIV_NODE_TYPE_FALLBACKS.get(node.tag, "")


def parse_label_tokens(value: str) -> list[str]:
    """Split N-attribute labels into token arrays."""

    if not value:
        return []
    tokens: list[str] = []
    for section in value.split("-"):
        for token in section.split("."):
            token = token.strip()
            if token:
                tokens.append(token)
    return tokens


def parse_appendix_label_tokens(value: str) -> list[str]:
    """Split appendix-style N labels by whitespace tokens."""

    if not value:
        return []
    return [token for token in value.split(" ") if token]
