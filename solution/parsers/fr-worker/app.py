import json
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, _context):
    records = event.get("Records", [])
    logger.info("FR worker received %s record(s)", len(records))

    for index, record in enumerate(records, start=1):
        body = record.get("body", "")
        logger.info("FR worker record %s body: %s", index, body)

    return {
        "statusCode": 200,
        "body": json.dumps({"processed": len(records)}),
    }
