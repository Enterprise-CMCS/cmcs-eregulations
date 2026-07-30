from common.config import (
    parse_credentials,
    parse_message_body,
    require_positive_int,
    unwrap_config,
)
from common.models import BackendCredentials
from models import EcfrPartConfig


def parse_config(payload: dict) -> EcfrPartConfig:
    config = unwrap_config(payload)

    return EcfrPartConfig(
        title_number=require_positive_int(config, "title_number"),
        part_number=require_positive_int(config, "part_number"),
        credentials=parse_credentials(config.get("credentials")),
    )


def parse_config_from_record(record: dict) -> EcfrPartConfig:
    payload = parse_message_body(record)
    return parse_config(payload)


__all__ = [
    "BackendCredentials",
    "EcfrPartConfig",
    "parse_config",
    "parse_config_from_record",
]
