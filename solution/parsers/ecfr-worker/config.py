"""Typed event/config parsing for eCFR worker messages.

This module enforces the queue contract produced by the eCFR launcher.
"""

from dataclasses import dataclass

from common.auth import BackendCredentials, resolve_backend_credentials
from common.config import (
    parse_typed_config_from_event,
    require_bool,
    require_non_empty_string,
    require_positive_int,
    unwrap_config,
)


@dataclass
class EcfrPartConfig:
    """Validated config object for one eCFR title/part processing unit."""

    title_number: int
    part_number: int
    effective_date: str
    upload_reg_text: bool
    upload_locations: bool
    credentials: BackendCredentials


def parse_config(payload: dict) -> EcfrPartConfig:
    """Parse and validate worker config payload into EcfrPartConfig."""

    config = unwrap_config(payload)

    return EcfrPartConfig(
        title_number=require_positive_int(config, "title_number"),
        part_number=require_positive_int(config, "part_number"),
        effective_date=require_non_empty_string(config, "effective_date"),
        upload_reg_text=require_bool(config, "upload_reg_text"),
        upload_locations=require_bool(config, "upload_locations"),
        credentials=resolve_backend_credentials(config.get("credentials")),
    )


def parse_config_from_event(event: dict) -> EcfrPartConfig:
    """Parse Lambda event (SQS or HTTP) into worker config."""

    return parse_typed_config_from_event(event, parse_config)


__all__ = [
    "BackendCredentials",
    "EcfrPartConfig",
    "parse_config",
    "parse_config_from_event",
]
