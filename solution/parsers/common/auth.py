import json
import os
from typing import Any

from common.config import ConfigParseError, parse_credentials
from common.models import BackendCredentials


def resolve_backend_credentials(raw_credentials: Any = None) -> BackendCredentials:
    if isinstance(raw_credentials, dict):
        parsed = _parse_message_credentials(raw_credentials)
        if parsed is not None:
            return parsed

    secret_name = os.environ.get("EREGS_AUTH_SECRET_NAME", "").strip()
    if secret_name:
        return _load_credentials_from_secret(secret_name)

    bearer_token = os.environ.get("EREGS_BEARER_TOKEN", "").strip()
    if bearer_token:
        return parse_credentials({"auth_type": "bearer", "token": bearer_token})

    username = os.environ.get("EREGS_USERNAME", "").strip()
    password = os.environ.get("EREGS_PASSWORD", "").strip()
    if username and password:
        return parse_credentials(
            {
                "auth_type": "basic",
                "username": username,
                "password": password,
            }
        )

    raise ConfigParseError(
        "Backend credentials are not configured; set EREGS_AUTH_SECRET_NAME, "
        "EREGS_BEARER_TOKEN, or EREGS_USERNAME/EREGS_PASSWORD"
    )


def _load_credentials_from_secret(secret_name: str) -> BackendCredentials:
    client = _get_secrets_client()
    response = client.get_secret_value(SecretId=secret_name)
    secret_string = response.get("SecretString")
    if not isinstance(secret_string, str) or not secret_string.strip():
        raise ConfigParseError("Secrets Manager secret must include non-empty SecretString JSON")

    try:
        payload = json.loads(secret_string)
    except json.JSONDecodeError as exc:
        raise ConfigParseError("Secrets Manager secret must contain valid JSON") from exc

    return parse_credentials(payload)


def _parse_message_credentials(raw_credentials: dict[str, Any]) -> BackendCredentials | None:
    try:
        return parse_credentials(raw_credentials)
    except ConfigParseError:
        return None


def _get_secrets_client():
    import boto3

    return boto3.client("secretsmanager")
