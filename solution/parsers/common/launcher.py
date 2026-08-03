import json
import os
from typing import Any


def is_local_mode() -> bool:
    return os.environ.get("PARSER_LOCAL_MODE", "false").lower() == "true"


def send_work_units(queue_url: str, work_units: list[dict[str, Any]]) -> None:
    sqs = _get_sqs_client()

    for work_unit in work_units:
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(work_unit),
        )


def dispatch_work_units(work_units: list[dict[str, Any]]) -> tuple[bool, int, list[dict[str, str]]]:
    local_mode = is_local_mode()

    if local_mode:
        worker_url = os.environ["PARSER_WORKER_URL"]
        succeeded, failures = send_work_units_via_http(worker_url, work_units)
        return local_mode, succeeded, failures

    queue_url = os.environ["PARSER_QUEUE_URL"]
    send_work_units(queue_url, work_units)
    return local_mode, len(work_units), []


def build_launcher_response(
    work_units: list[dict[str, Any]],
    local_mode: bool,
    succeeded: int,
    failures: list[dict[str, str]],
) -> dict[str, Any]:
    payload = {
        "enqueued": len(work_units),
        "local_mode": local_mode,
        "succeeded": succeeded,
        "failed": len(failures),
        "failures": failures,
        "work_units": work_units,
    }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(payload),
    }


def send_work_units_via_http(
    worker_url: str,
    work_units: list[dict[str, Any]],
    timeout: int = 60,
) -> tuple[int, list[dict[str, str]]]:
    success = 0
    failures = []

    for index, work_unit in enumerate(work_units):
        try:
            resp = _http_post(
                worker_url,
                data=json.dumps(work_unit),
                timeout=timeout,
            )
            if resp.status_code != 200 and hasattr(resp, "text") and resp.text:
                raise RuntimeError(f"POST failed with {resp.status_code}: {resp.text}")
            resp.raise_for_status()
            success += 1
        except Exception as exc:
            failures.append(
                {
                    "index": str(index),
                    "reason": str(exc),
                }
            )

    return success, failures


def _get_sqs_client():
    import boto3

    return boto3.client("sqs")


def _http_post(url: str, data: str, timeout: int):
    import requests

    return requests.post(url, data=data, timeout=timeout)
