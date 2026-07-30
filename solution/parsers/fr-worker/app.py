import json
import logging

from common.config import parse_message_body, require_single_record
from config import parse_config


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, _context):
    records = event.get("Records", [])
    record = require_single_record(records)
    payload = parse_message_body(record)
    config = parse_config(payload)

    logger.info(
        "Parsed FR work item: document_number=%s",
        config.document_number,
    )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "processed": 1,
                "document_number": config.document_number,
            }
        ),
    }
