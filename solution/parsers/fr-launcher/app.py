import json
import logging
import os
from datetime import datetime, timezone

from common.launcher import (
    build_basic_credentials_from_env,
    build_launcher_response,
    is_local_mode,
    send_work_units,
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _build_work_units(run_time: str) -> list[dict]:
    return [
        {
            "config": {
                "document_number": "placeholder-doc",
                "credentials": build_basic_credentials_from_env(),
                "scheduled_at": run_time,
            }
        }
    ]


def handler(event, _context):
    run_time = datetime.now(timezone.utc).isoformat()
    work_units = _build_work_units(run_time)
    local_mode = is_local_mode()

    if local_mode:
        logger.info("FR launcher local mode enabled; skipping SQS send")
    else:
        queue_url = os.environ["PARSER_QUEUE_URL"]
        send_work_units(queue_url, work_units)
        logger.info("FR launcher enqueued %s work unit(s)", len(work_units))

    logger.info("FR launcher trigger event: %s", json.dumps(event))

    return build_launcher_response(work_units, local_mode)
