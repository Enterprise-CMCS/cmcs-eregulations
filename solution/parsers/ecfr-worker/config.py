from dataclasses import dataclass

from common.auth import resolve_backend_credentials
from common.config import parse_typed_config_from_event, require_positive_int, unwrap_config
from common.auth import BackendCredentials


@dataclass
class EcfrPartConfig:
    title_number: int
    part_number: int
    credentials: BackendCredentials


def parse_config(payload: dict) -> EcfrPartConfig:
    config = unwrap_config(payload)

    return EcfrPartConfig(
        title_number=require_positive_int(config, "title_number"),
        part_number=require_positive_int(config, "part_number"),
        credentials=resolve_backend_credentials(config.get("credentials")),
    )


def parse_config_from_event(event: dict) -> EcfrPartConfig:
    return parse_typed_config_from_event(event, parse_config)


__all__ = [
    "BackendCredentials",
    "EcfrPartConfig",
    "parse_config",
    "parse_config_from_event",
]
