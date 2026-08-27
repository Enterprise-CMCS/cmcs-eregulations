import json
import logging
import os

from common.auth import resolve_backend_credentials
from common.config import ConfigParseError, require_non_empty_string
from common.eregs_config import fetch_parser_config
from common.launcher import (
    build_launcher_response,
    dispatch_work_units,
)
from common.logging import resolve_log_level_name


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _resolve_parser_log_level(parser_config: dict) -> str:
    try:
        configured = require_non_empty_string(parser_config, "loglevel")
        return resolve_log_level_name(configured)
    except ConfigParseError as exc:
        raise RuntimeError(str(exc)) from exc


def _build_work_units(parser_log_level: str) -> list[dict]:
    return [
        {
            "config": {
                "document_number": "placeholder-doc",
                "log_level": parser_log_level,
            }
        }
    ]


def handler(event, _context):
    logger.info("FR launcher trigger event: %s", json.dumps(event))

    credentials = resolve_backend_credentials()
    logger.info("FR launcher credentials resolved with auth_type=%s", credentials.auth_type)

    parser_config = fetch_parser_config(api_base_url=os.environ["EREGS_API_URL_V3"], credentials=credentials)
    parser_log_level = _resolve_parser_log_level(parser_config)
    logger.setLevel(getattr(logging, parser_log_level))
    logger.info("FR launcher parser-config loglevel resolved: %s", parser_log_level)

    work_units = _build_work_units(parser_log_level)
    local_mode, succeeded, failures = dispatch_work_units(work_units)
    if local_mode:
        logger.info("FR launcher sent %s/%s work unit(s) to local worker", succeeded, len(work_units))
    else:
        logger.info("FR launcher enqueued %s work unit(s)", len(work_units))

    return build_launcher_response(
        work_units=work_units,
        local_mode=local_mode,
        succeeded=succeeded,
        failures=failures,
    )
