import json
import logging

from .config import parse_config_from_event


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, _context):
    config = parse_config_from_event(event)

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
