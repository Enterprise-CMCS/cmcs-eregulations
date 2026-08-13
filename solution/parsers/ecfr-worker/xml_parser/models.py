"""Intermediate node models for eCFR XML parsing.

These dataclasses intentionally model only top-level parser concepts and serve
as placeholders for fuller legacy parity implementation.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PartNode:
    """Top-level parsed representation for one regulation part document."""

    title_number: int
    part_number: int
    node_type: str = "part"
    label: list[str] = field(default_factory=list)
    title: str = ""
    children: list[dict[str, Any]] = field(default_factory=list)
    authority: dict[str, Any] | None = None
    source: dict[str, Any] | None = None
    editorial_note: dict[str, Any] | None = None
