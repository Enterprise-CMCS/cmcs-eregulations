import json
import logging

from .config import parse_config_from_event


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _configure_logging(log_level_name: str | None = None) -> None:
    if log_level_name is None:
        log_level_name = "INFO"

    log_level = getattr(logging, log_level_name, logging.INFO)
    logging.basicConfig(level=log_level)
    logger.setLevel(log_level)


_configure_logging()


def handler(event, _context):
    config = parse_config_from_event(event)
    _configure_logging(config.log_level)

    logger.info(
        "Parsed FR work item: document_number=%s",
        config.document_number,
    )

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(
            {
                "processed": 1,
                "document_number": config.document_number,
            }
        ),
    }
