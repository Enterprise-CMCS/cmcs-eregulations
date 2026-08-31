"""Typed event/config parsing for FR worker messages.

This module enforces the queue contract produced by the FR launcher.
"""

from dataclasses import dataclass
from typing import Any

from common.config import (
    ConfigParseError,
    parse_typed_config_from_event,
    require_non_empty_string,
    require_positive_int,
    unwrap_config,
)
from common.logging import resolve_log_level_name

from common.auth import BackendCredentials, resolve_backend_credentials


@dataclass
class FrDocumentConfig:
    """Validated config object for one Federal Register document."""

    document_number: str
    title: int
    part: str
    description: str
    name: str
    doc_type: str
    url: str
    date: str
    docket_numbers: list[str]
    raw_text_url: str
    full_text_xml_url: str
    log_level: str
    credentials: BackendCredentials


def parse_config(payload: dict) -> FrDocumentConfig:
    """Parse and validate worker config payload into FrDocumentConfig."""

    config = unwrap_config(payload)

    return FrDocumentConfig(
        document_number=require_non_empty_string(config, "document_number"),
        title=require_positive_int(config, "title"),
        part=require_non_empty_string(config, "part"),
        description=require_non_empty_string(config, "description"),
        name=require_non_empty_string(config, "name"),
        doc_type=require_non_empty_string(config, "doc_type"),
        url=require_non_empty_string(config, "url"),
        date=require_non_empty_string(config, "date"),
        docket_numbers=_require_string_list(config),
        raw_text_url=require_non_empty_string(config, "raw_text_url"),
        full_text_xml_url=require_non_empty_string(config, "full_text_xml_url"),
        log_level=_require_log_level(config),
        credentials=resolve_backend_credentials(),
    )


def parse_config_from_event(event: dict) -> FrDocumentConfig:
    """Parse Lambda event (SQS or HTTP) into worker config."""

    return parse_typed_config_from_event(event, parse_config)


def _require_string_list(config: dict) -> list[str]:
    """Require docket_numbers to be a list of non-empty strings."""

    value = config.get("docket_numbers")
    if not isinstance(value, list):
        raise ConfigParseError("docket_numbers must be a list")
    return [require_non_empty_string_str(item) for item in value]


def require_non_empty_string_str(value: Any) -> str:
    """Require a single value to be a non-empty string."""

    if not isinstance(value, str) or not value.strip():
        raise ConfigParseError("docket_numbers entries must be non-empty strings")
    return value.strip()


def _require_log_level(config: dict) -> str:
    """Validate and normalize log_level for worker runtime logging."""

    value = require_non_empty_string(config, "log_level")
    return resolve_log_level_name(value)


__all__ = [
    "BackendCredentials",
    "FrDocumentConfig",
    "parse_config",
    "parse_config_from_event",
]
