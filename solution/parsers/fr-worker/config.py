from common.config import parse_credentials, require_non_empty_string, unwrap_config
from models import FrDocumentConfig


def parse_config(payload: dict) -> FrDocumentConfig:
    config = unwrap_config(payload)

    return FrDocumentConfig(
        document_number=require_non_empty_string(config, "document_number"),
        credentials=parse_credentials(config.get("credentials")),
    )


__all__ = [
    "FrDocumentConfig",
    "parse_config",
]
