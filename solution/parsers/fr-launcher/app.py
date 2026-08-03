import json
import logging
import os
from datetime import datetime, timezone

from common.auth import resolve_backend_credentials
from common.launcher import (
    build_launcher_response,
    is_local_mode,
    send_work_units,
    send_work_units_via_http,
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _build_work_units(run_time: str) -> list[dict]:
    return [
        {
            "config": {
                "document_number": "placeholder-doc",
                "scheduled_at": run_time,
            }
        }
    ]


def handler(event, _context):
    run_time = datetime.now(timezone.utc).isoformat()
    work_units = _build_work_units(run_time)
    credentials = resolve_backend_credentials()
    local_mode = is_local_mode()
    failures = []
    succeeded = 0

    logger.info("FR launcher credentials resolved with auth_type=%s", credentials.auth_type)

    if local_mode:
        worker_url = os.environ["PARSER_WORKER_URL"]
        succeeded, failures = send_work_units_via_http(worker_url, work_units)
        logger.info("FR launcher sent %s/%s work unit(s) to local worker", succeeded, len(work_units))
    else:
        queue_url = os.environ["PARSER_QUEUE_URL"]
        send_work_units(queue_url, work_units)
        succeeded = len(work_units)
        logger.info("FR launcher enqueued %s work unit(s)", len(work_units))

    logger.info("FR launcher trigger event: %s", json.dumps(event))

    return build_launcher_response(
        work_units=work_units,
        local_mode=local_mode,
        succeeded=succeeded,
        failures=failures,
    )
