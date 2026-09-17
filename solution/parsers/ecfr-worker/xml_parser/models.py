"""Intermediate node models for eCFR XML parsing.

These typed structures define the normalized node contracts used across parsing,
post-processing, and final document normalization.
"""

from dataclasses import dataclass, field
from typing import Literal, TypedDict, TypeAlias


class ContainerNode(TypedDict):
    """Container node shape for hierarchy-carrying XML nodes."""

    node_type: str
    label: list[str]
    title: str
    children: list["XmlNode"]


class ParagraphNode(TypedDict):
    """Paragraph node shape with optional parsed marker/citation labels."""

    node_type: Literal["Paragraph"]
    text: str
    label: list[str]
    marker: list[str]


class FlushParagraphNode(TypedDict):
    """Flush paragraph node shape."""

    node_type: Literal["FlushParagraph"]
    text: str


class ImageNode(TypedDict):
    """Embedded image node shape."""

    node_type: Literal["Image"]
    src: str


class ContentNode(TypedDict):
    """Generic rich-content node shape."""

    node_type: str
    content: str


class EffectiveDateNoteNode(TypedDict):
    """Effective date note node shape."""

    node_type: Literal["EffectiveDateNote"]
    header: str
    content: str


class MetadataNode(TypedDict):
    """Top-level metadata node shape (authority/source/editorial note)."""

    node_type: Literal["Authority", "Source", "EdNote"]
    header: str
    content: str


class UnknownNode(TypedDict):
    """Fallback shape for unknown node types after strict normalization."""

    node_type: str
    children: list["XmlNode"]


XmlNode: TypeAlias = (
    ContainerNode
    | ParagraphNode
    | FlushParagraphNode
    | ImageNode
    | ContentNode
    | EffectiveDateNoteNode
    | UnknownNode
)


@dataclass
class PartNode:
    """Top-level parsed representation for one regulation part document."""

    title_number: int
    part_number: int
    node_type: Literal["PART"] = "PART"
    label: list[str] = field(default_factory=list)
    title: str = ""
    children: list[XmlNode] = field(default_factory=list)
    authority: MetadataNode | None = None
    source: MetadataNode | None = None
    editorial_note: MetadataNode | None = None

    def __post_init__(self) -> None:
        """Validate strict top-level part model invariants."""

        if not isinstance(self.title_number, int) or self.title_number <= 0:
            raise ValueError("title_number must be a positive integer")
        if not isinstance(self.part_number, int) or self.part_number <= 0:
            raise ValueError("part_number must be a positive integer")
        if self.node_type != "PART":
            raise ValueError('node_type must be exactly "PART"')
        if not isinstance(self.label, list) or any(not isinstance(item, str) for item in self.label):
            raise ValueError("label must be a list of strings")
