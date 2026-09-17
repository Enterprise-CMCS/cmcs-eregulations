"""Shared parser logging helpers."""

import logging

from common.config import ConfigParseError, require_non_empty_string

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
            "loglevel must be one of fatal, error, warn(ing), info, debug, trace, critical; got: %r" % value
        )
    return resolved


def resolve_parser_log_level(parser_config: dict) -> str:
    """Resolve and validate the parser log level from a parser-config object.

    Returns a stdlib logging level name (e.g. "INFO"). Raises RuntimeError when
    the config value is missing or not a recognizable log level.
    """

    try:
        configured = require_non_empty_string(parser_config, "loglevel")
        return resolve_log_level_name(configured)
    except ConfigParseError as exc:
        raise RuntimeError(str(exc)) from exc


def resolve_work_unit_log_level(config_data: dict) -> str:
    """Validate and normalize a worker work-unit `log_level` value.

    Reads the `log_level` key (set by the launcher from parser config) and
    returns the corresponding stdlib logging level name.
    """

    value = require_non_empty_string(config_data, "log_level")
    return resolve_log_level_name(value)


def configure_runtime_logging(log_level_name: str | None, module_logger: logging.Logger) -> None:
    """Configure root and module logging for parser worker execution."""

    if log_level_name is None:
        log_level_name = "INFO"

    log_level = getattr(logging, log_level_name, logging.INFO)
    logging.basicConfig(level=log_level)
    module_logger.setLevel(log_level)
