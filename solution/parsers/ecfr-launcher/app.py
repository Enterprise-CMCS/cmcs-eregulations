import json
import logging
from datetime import datetime, timezone

from common.auth import resolve_backend_credentials
from common.launcher import (
    build_launcher_response,
    dispatch_work_units,
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _build_work_units(run_time: str) -> list[dict]:
    return [
        {
            "config": {
                "title_number": 42,
                "part_number": 400,
                "scheduled_at": run_time,
            }
        }
    ]


def handler(event, _context):
    run_time = datetime.now(timezone.utc).isoformat()
    logger.info("eCFR launcher trigger event: %s", json.dumps(event))

    credentials = resolve_backend_credentials()
    logger.info("eCFR launcher credentials resolved with auth_type=%s", credentials.auth_type)

    work_units = _build_work_units(run_time)
    local_mode, succeeded, failures = dispatch_work_units(work_units)
    if local_mode:
        logger.info("eCFR launcher sent %s/%s work unit(s) to local worker", succeeded, len(work_units))
    else:
        logger.info("eCFR launcher enqueued %s work unit(s)", len(work_units))

    return build_launcher_response(
        work_units=work_units,
        local_mode=local_mode,
        succeeded=succeeded,
        failures=failures,
    )
