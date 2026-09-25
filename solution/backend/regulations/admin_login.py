"""Runtime access control for Django's password-based admin login."""

import json
import secrets
import time

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings

_CACHE_TTL_SECONDS = 60
_CYPRESS_SESSION_GRANT_SECONDS = 300
_CYPRESS_SESSION_KEY = "cypress_admin_login_grant_expires_at"
_cache_expires_at = 0.0
_cached_manual_enabled = False
_cached_cypress_token = None


def is_admin_login_enabled(request):
    """Return whether this request may access the Django admin login form."""

    local_override = getattr(settings, "ADMIN_LOGIN_LOCAL_OVERRIDE", None)
    if local_override is not None:
        return _is_enabled_value(local_override)

    manual_enabled, cypress_token = _get_cached_access_configuration()
    return manual_enabled or _has_cypress_session_grant(request) or _has_valid_cypress_token(request, cypress_token)


def grant_cypress_admin_login_session(request):
    """Grant this browser a brief login-form session after a valid Cypress token request."""

    _, cypress_token = _get_cached_access_configuration()
    if _has_valid_cypress_token(request, cypress_token):
        request.session[_CYPRESS_SESSION_KEY] = time.time() + _CYPRESS_SESSION_GRANT_SECONDS


def _get_cached_access_configuration():
    """Read and briefly cache the fail-closed SSM flag and Cypress token."""

    global _cache_expires_at, _cached_cypress_token, _cached_manual_enabled

    if time.monotonic() < _cache_expires_at:
        return _cached_manual_enabled, _cached_cypress_token

    _cached_manual_enabled = _get_manual_enabled_flag()
    _cached_cypress_token = _get_cypress_token()
    _cache_expires_at = time.monotonic() + _CACHE_TTL_SECONDS
    return _cached_manual_enabled, _cached_cypress_token


def _get_manual_enabled_flag():
    parameter_name = getattr(settings, "ADMIN_LOGIN_ENABLED_PARAMETER", "")
    if not parameter_name:
        return False

    try:
        response = boto3.client("ssm").get_parameter(Name=parameter_name, WithDecryption=False)
        return _is_enabled_value(response["Parameter"]["Value"])
    except (BotoCoreError, ClientError, KeyError, TypeError):
        return False


def _get_cypress_token():
    secret_name = getattr(settings, "ADMIN_LOGIN_CYPRESS_TOKEN_SECRET", "")
    if not secret_name:
        return None

    try:
        response = boto3.client("secretsmanager").get_secret_value(SecretId=secret_name)
        token = json.loads(response["SecretString"])["token"]
        return token if isinstance(token, str) and token else None
    except (BotoCoreError, ClientError, json.JSONDecodeError, KeyError, TypeError):
        return None


def _is_enabled_value(value):
    return isinstance(value, str) and value.strip().lower() == "true"


def _has_cypress_session_grant(request):
    expires_at = request.session.get(_CYPRESS_SESSION_KEY)
    return isinstance(expires_at, (int, float)) and expires_at >= time.time()


def _has_valid_cypress_token(request, cypress_token):
    request_token = request.headers.get("X-eRegs-Cypress-Admin-Token", "")
    return isinstance(cypress_token, str) and bool(request_token) and secrets.compare_digest(request_token, cypress_token)


def clear_admin_login_cache():
    """Clear cached AWS access configuration for tests."""

    global _cache_expires_at, _cached_cypress_token, _cached_manual_enabled

    _cache_expires_at = 0.0
    _cached_manual_enabled = False
    _cached_cypress_token = None
