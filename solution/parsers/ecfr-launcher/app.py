import json
import logging
import os
from datetime import datetime, timezone

import boto3


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

sqs = boto3.client("sqs")


def handler(event, _context):
    queue_url = os.environ["PARSER_QUEUE_URL"]
    run_time = datetime.now(timezone.utc).isoformat()

    work_units = [
        {
            "parser": "ecfr",
            "unit_type": "title-part",
            "title": 42,
            "part": "400",
            "scheduled_at": run_time,
        }
    ]

    for work_unit in work_units:
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(work_unit),
        )

    logger.info("eCFR launcher enqueued %s work unit(s)", len(work_units))
    logger.info("eCFR launcher trigger event: %s", json.dumps(event))

    return {"statusCode": 200, "enqueued": len(work_units)}
