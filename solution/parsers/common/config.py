"""Shared payload parsing utilities for parser Lambdas.

The parser services are invoked through both SQS events and lambda-proxy HTTP
events in local mode. These helpers normalize both forms into one config shape.
"""

import json
from typing import TYPE_CHECKING, Any, Callable, TypeVar

if TYPE_CHECKING:
    from common.auth import BackendCredentials


class ConfigParseError(ValueError):
    """Raised when incoming Lambda payload/config cannot be parsed safely."""

    pass


TConfig = TypeVar("TConfig")


def parse_message_body(record: dict[str, Any]) -> dict[str, Any]:
    """Parse and validate an SQS record body into a JSON object."""

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
    """Return payload['config'] when present, otherwise payload itself."""

    config = payload.get("config", payload)
    if not isinstance(config, dict):
        raise ConfigParseError("config must be a JSON object")
    return config


def require_single_record(records: list[Any]) -> dict[str, Any]:
    """Validate that exactly one SQS record is present."""

    if len(records) != 1:
        raise ConfigParseError(f"Expected exactly 1 SQS record, found {len(records)}")

    record = records[0]
    if not isinstance(record, dict):
        raise ConfigParseError("SQS record must be a JSON object")

    return record


def parse_credentials(raw_credentials: Any) -> "BackendCredentials":
    """Parse credential payload into BackendCredentials."""

    from common.auth import BackendCredentials

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
    """Require a positive integer value for a config key."""

    value = data.get(key)
    if not isinstance(value, int) or value <= 0:
        raise ConfigParseError(f"{key} must be a positive integer")
    return value


def require_non_empty_string(data: dict[str, Any], key: str) -> str:
    """Require a non-empty string value for a config key."""

    return require_non_empty_string_value(data.get(key), f"{key} must be a non-empty string")


def require_non_empty_string_value(value: Any, error_message: str) -> str:
    """Require a standalone value to be a non-empty string."""

    if not isinstance(value, str) or not value.strip():
        raise ConfigParseError(error_message)
    return value.strip()


def require_bool(data: dict[str, Any], key: str) -> bool:
    """Require a boolean value for a config key."""

    value = data.get(key)
    if not isinstance(value, bool):
        raise ConfigParseError(f"{key} must be a boolean")
    return value


def require_bool_config(data: dict[str, Any], key: str) -> bool:
    """Require a boolean parser-config value, raising RuntimeError on failure."""

    try:
        return require_bool(data, key)
    except ConfigParseError as exc:
        raise RuntimeError(str(exc)) from exc


def parse_payload_from_event(event: dict[str, Any]) -> dict[str, Any]:
    """Normalize SQS or lambda-proxy event wrappers into one payload object."""

    if not isinstance(event, dict):
        raise ConfigParseError("Lambda event must be a JSON object")

    records = event.get("Records")
    if isinstance(records, list):
        record = require_single_record(records)
        return parse_message_body(record)

    body = event.get("body")
    if body is None:
        raise ConfigParseError("Lambda event must include either 'Records' or 'body'")

    if isinstance(body, str):
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            raise ConfigParseError("Lambda event body must contain valid JSON") from exc
    elif isinstance(body, dict):
        payload = body
    else:
        raise ConfigParseError("Lambda event body must be a JSON object or JSON string")

    if not isinstance(payload, dict):
        raise ConfigParseError("Lambda event payload must be a JSON object")

    return payload


def parse_typed_config_from_event(
    event: dict[str, Any],
    parse_config: Callable[[dict[str, Any]], TConfig],
) -> TConfig:
    """Normalize event payload and apply a service-specific config parser."""

    payload = parse_payload_from_event(event)
    return parse_config(payload)
