import json
import logging
import os
from datetime import datetime, timezone

import boto3


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _is_local_mode() -> bool:
    return os.environ.get("PARSER_LOCAL_MODE", "false").lower() == "true"


def _build_work_units(run_time: str) -> list[dict]:
    return [
        {
            "config": {
                "title_number": 42,
                "part_number": 400,
                "credentials": {
                    "auth_type": "basic",
                    "username": os.environ.get("EREGS_USERNAME", ""),
                    "password": os.environ.get("EREGS_PASSWORD", ""),
                },
                "scheduled_at": run_time,
            }
        }
    ]


def _send_work_units(queue_url: str, work_units: list[dict]) -> None:
    sqs = boto3.client("sqs")

    for work_unit in work_units:
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(work_unit),
        )


def handler(event, _context):
    run_time = datetime.now(timezone.utc).isoformat()
    work_units = _build_work_units(run_time)

    if _is_local_mode():
        logger.info("eCFR launcher local mode enabled; skipping SQS send")
    else:
        queue_url = os.environ["PARSER_QUEUE_URL"]
        _send_work_units(queue_url, work_units)
        logger.info("eCFR launcher enqueued %s work unit(s)", len(work_units))

    logger.info("eCFR launcher trigger event: %s", json.dumps(event))

    return {
        "statusCode": 200,
        "enqueued": len(work_units),
        "local_mode": _is_local_mode(),
        "work_units": work_units,
    }
