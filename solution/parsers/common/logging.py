"""Shared parser logging helpers."""

from common.config import ConfigParseError


_LOG_LEVEL_MAP = {
    "fatal": "CRITICAL",
    "error": "ERROR",
    "warn": "WARNING",
    "warning": "WARNING",
    "info": "INFO",
    "debug": "DEBUG",
    "trace": "DEBUG",
    "critical": "CRITICAL",
}


def resolve_log_level_name(value: str) -> str:
    """Normalize parser-config loglevel values to stdlib logging names."""

    normalized = value.strip().lower()
    resolved = _LOG_LEVEL_MAP.get(normalized)
    if resolved is None:
        raise ConfigParseError(
            "loglevel must be one of fatal, error, warn, info, debug, trace"
        )
    return resolved
