"""Credential helpers shared by parser launcher/worker Lambdas.

This module centralizes how parser services resolve eRegs auth credentials
from event payloads, AWS Secrets Manager, and environment variables.
"""

import json
import os
import base64
from dataclasses import dataclass
from typing import Any

from common.config import ConfigParseError, parse_credentials


@dataclass
class BackendCredentials:
    """Normalized backend authentication credentials."""

    auth_type: str
    username: str | None = None
    password: str | None = None
    token: str | None = None


def resolve_backend_credentials(raw_credentials: Any = None) -> BackendCredentials:
    """Resolve credentials for outbound eRegs calls.

    Resolution order is intentionally strict and shared across launchers/workers:
    message payload -> Secrets Manager -> bearer env var -> basic env vars.
    """

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


def build_auth_headers(credentials: BackendCredentials) -> dict[str, str]:
    """Convert normalized credentials into an HTTP Authorization header."""

    if credentials.auth_type == "bearer" and credentials.token:
        return {
            "Authorization": f"Bearer {credentials.token}",
        }

    if credentials.auth_type == "basic" and credentials.username and credentials.password:
        raw = f"{credentials.username}:{credentials.password}".encode("utf-8")
        encoded = base64.b64encode(raw).decode("utf-8")
        return {
            "Authorization": f"Basic {encoded}",
        }

    raise ConfigParseError("backend credentials are not valid for authorization headers")


def _load_credentials_from_secret(secret_name: str) -> BackendCredentials:
    """Load and parse credentials JSON from AWS Secrets Manager."""

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
    """Attempt to parse message credentials; return None if invalid."""

    try:
        return parse_credentials(raw_credentials)
    except ConfigParseError:
        return None


def _get_secrets_client():
    """Create a Secrets Manager client."""

    import boto3

    return boto3.client("secretsmanager")
