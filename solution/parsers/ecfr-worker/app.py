import json
import logging

from common.config import require_single_record
from config import parse_config_from_record


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, _context):
    records = event.get("Records", [])
    record = require_single_record(records)
    config = parse_config_from_record(record)

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
