"""Identifier parsing helpers used by eCFR structure normalization/extraction."""

from typing import Any


def identifier_tokens(identifier: Any) -> list[str]:
    """Normalize identifier strings/lists into non-empty token lists."""

    if isinstance(identifier, str):
        value = identifier.strip()
        if not value:
            return []
        tokens: list[str] = []
        for piece in value.split("."):
            segment = piece.strip()
            if not segment:
                continue
            tokens.extend(token for token in segment.split(" ") if token)
        return tokens

    if isinstance(identifier, list):
        tokens: list[str] = []
        for item in identifier:
            if isinstance(item, str) and item.strip():
                tokens.append(item.strip())
        return tokens

    return []


def first_identifier_token(identifier: Any) -> str | None:
    """Return first identifier token from eCFR identifier values."""

    tokens = identifier_tokens(identifier)
    if not tokens:
        return None
    return tokens[0]


def parse_section_identifier(identifier: Any, fallback_part_str: str) -> tuple[str, str | None]:
    """Split eCFR section identifiers into part and section components."""

    tokens = identifier_tokens(identifier)
    if not tokens:
        return fallback_part_str, None

    if len(tokens) == 1:
        value = tokens[0]
        if "." in value:
            first, rest = value.split(".", 1)
            if first and rest:
                return first, rest
        return fallback_part_str, value

    return tokens[0], ".".join(tokens[1:])
