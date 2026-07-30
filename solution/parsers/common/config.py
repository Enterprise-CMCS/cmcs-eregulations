import json
from typing import Any

from common.models import BackendCredentials


class ConfigParseError(ValueError):
    pass


def parse_message_body(record: dict[str, Any]) -> dict[str, Any]:
    body = record.get("body")
    if not body or not isinstance(body, str):
        raise ConfigParseError("SQS record body must be a non-empty JSON string")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ConfigParseError("SQS record body must contain valid JSON") from exc

    if not isinstance(payload, dict):
        raise ConfigParseError("SQS record payload must be a JSON object")

    return payload


def unwrap_config(payload: dict[str, Any]) -> dict[str, Any]:
    config = payload.get("config", payload)
    if not isinstance(config, dict):
        raise ConfigParseError("config must be a JSON object")
    return config


def require_single_record(records: list[Any]) -> dict[str, Any]:
    if len(records) != 1:
        raise ConfigParseError(f"Expected exactly 1 SQS record, found {len(records)}")

    record = records[0]
    if not isinstance(record, dict):
        raise ConfigParseError("SQS record must be a JSON object")

    return record


def parse_credentials(raw_credentials: Any) -> BackendCredentials:
    if not isinstance(raw_credentials, dict):
        raise ConfigParseError("credentials must be a JSON object")

    auth_type = raw_credentials.get("auth_type", "basic")
    if auth_type == "basic":
        username = require_non_empty_string(raw_credentials, "username")
        password = require_non_empty_string(raw_credentials, "password")
        return BackendCredentials(auth_type=auth_type, username=username, password=password)

    if auth_type == "bearer":
        token = require_non_empty_string(raw_credentials, "token")
        return BackendCredentials(auth_type=auth_type, token=token)

    raise ConfigParseError("credentials.auth_type must be 'basic' or 'bearer'")


def require_positive_int(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int) or value <= 0:
        raise ConfigParseError(f"{key} must be a positive integer")
    return value


def require_non_empty_string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigParseError(f"{key} must be a non-empty string")
    return value.strip()
