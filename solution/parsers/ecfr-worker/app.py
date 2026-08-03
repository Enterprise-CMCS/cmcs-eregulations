import json
import logging

from .config import parse_config_from_event


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, _context):
    config = parse_config_from_event(event)

    logger.info(
        "Parsed eCFR work item: title=%s part=%s",
        config.title_number,
        config.part_number,
    )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "processed": 1,
                "title_number": config.title_number,
                "part_number": config.part_number,
            }
        ),
    }
