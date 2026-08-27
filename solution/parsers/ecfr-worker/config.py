"""Typed event/config parsing for eCFR worker messages.

This module enforces the queue contract produced by the eCFR launcher.
"""

from dataclasses import dataclass
from datetime import datetime

from common.auth import BackendCredentials, resolve_backend_credentials
from common.config import (
    ConfigParseError,
    parse_typed_config_from_event,
    require_bool,
    require_non_empty_string,
    require_positive_int,
    unwrap_config,
)
from common.logging import resolve_log_level_name


@dataclass
class EcfrPartConfig:
    """Validated config object for one eCFR title/part processing unit."""

    title_number: int
    part_number: int
    effective_date: str
    upload_reg_text: bool
    upload_locations: bool
    log_level: str
    credentials: BackendCredentials


def parse_config(payload: dict) -> EcfrPartConfig:
    """Parse and validate worker config payload into EcfrPartConfig."""

    config = unwrap_config(payload)

    return EcfrPartConfig(
        title_number=require_positive_int(config, "title_number"),
        part_number=require_positive_int(config, "part_number"),
        effective_date=_require_effective_date(config),
        upload_reg_text=require_bool(config, "upload_reg_text"),
        upload_locations=require_bool(config, "upload_locations"),
        log_level=_require_log_level(config),
        credentials=resolve_backend_credentials(),
    )


def parse_config_from_event(event: dict) -> EcfrPartConfig:
    """Parse Lambda event (SQS or HTTP) into worker config."""

    return parse_typed_config_from_event(event, parse_config)


def _require_effective_date(config: dict) -> str:
    """Validate effective_date as strict YYYY-MM-DD text."""

    value = require_non_empty_string(config, "effective_date")
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise ConfigParseError("effective_date must be in YYYY-MM-DD format") from exc

    return value


def _require_log_level(config: dict) -> str:
    """Validate and normalize log_level for worker runtime logging."""

    value = require_non_empty_string(config, "log_level")
    return resolve_log_level_name(value)


__all__ = [
    "BackendCredentials",
    "EcfrPartConfig",
    "parse_config",
    "parse_config_from_event",
]
