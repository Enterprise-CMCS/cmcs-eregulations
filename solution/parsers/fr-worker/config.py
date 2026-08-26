from dataclasses import dataclass

from common.auth import resolve_backend_credentials
from common.auth import BackendCredentials
from common.config import parse_typed_config_from_event, require_non_empty_string, unwrap_config
from common.logging import resolve_log_level_name


@dataclass
class FrDocumentConfig:
    document_number: str
    log_level: str
    credentials: BackendCredentials


def parse_config(payload: dict) -> FrDocumentConfig:
    config = unwrap_config(payload)

    return FrDocumentConfig(
        document_number=require_non_empty_string(config, "document_number"),
        log_level=_require_log_level(config),
        credentials=resolve_backend_credentials(),
    )


def _require_log_level(config: dict) -> str:
    value = require_non_empty_string(config, "log_level")
    return resolve_log_level_name(value)


def parse_config_from_event(event: dict) -> FrDocumentConfig:
    return parse_typed_config_from_event(event, parse_config)


__all__ = [
    "FrDocumentConfig",
    "parse_config",
    "parse_config_from_event",
]
