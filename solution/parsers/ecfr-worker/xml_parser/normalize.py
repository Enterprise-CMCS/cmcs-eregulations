"""Normalization from XML parser intermediate models to eRegs document payloads."""

from typing import Any

from .models import PartNode


def normalize_part_for_eregs(part: PartNode) -> dict[str, Any]:
    """Convert parsed and post-processed part model into eRegs document JSON.

    This skeleton preserves a minimal stable shape while leaving detailed node
    normalization for follow-up implementation.
    """

    return {
        "node_type": part.node_type,
        "label": part.label,
        "title": part.title,
        "children": part.children,
        "authority": part.authority,
        "source": part.source,
        "editorial_note": part.editorial_note,
    }
