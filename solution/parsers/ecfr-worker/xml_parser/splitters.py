"""Paragraph content splitters aligned with eCFR marker behavior."""

import re

_SPLIT_NEXT_MARKER_RE = re.compile(
    r"^\([^\)]+\)\s*(?:<I>[^<]+</I>)?(?:[^\w\d]|(?:&[a-zA-Z0-9#]+;))*(\([^\)]+\))"
)


def split_paragraph_node(content: str) -> list[dict[str, str]]:
    """Split multi-marker paragraph content into separate paragraph nodes."""

    paragraphs: list[dict[str, str]] = []
    current = content

    while True:
        match = _SPLIT_NEXT_MARKER_RE.search(current)
        if match is None:
            break

        next_marker_start = match.start(1)
        next_marker_end = match.end(1)
        if next_marker_start <= 0:
            break

        if current[next_marker_end:].strip().startswith("[Reserved]"):
            break

        first = current[:next_marker_start]
        second = current[next_marker_start:]
        paragraphs.append({"node_type": "Paragraph", "text": first})
        current = second

    paragraphs.append({"node_type": "Paragraph", "text": current})
    return paragraphs
