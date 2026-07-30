import json
import os
from typing import Any


def is_local_mode() -> bool:
    return os.environ.get("PARSER_LOCAL_MODE", "false").lower() == "true"


def build_basic_credentials_from_env() -> dict[str, str]:
    return {
        "auth_type": "basic",
        "username": os.environ.get("EREGS_USERNAME", ""),
        "password": os.environ.get("EREGS_PASSWORD", ""),
    }


def send_work_units(queue_url: str, work_units: list[dict[str, Any]]) -> None:
    sqs = _get_sqs_client()

    for work_unit in work_units:
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(work_unit),
        )


def build_launcher_response(work_units: list[dict[str, Any]], local_mode: bool) -> dict[str, Any]:
    return {
        "statusCode": 200,
        "enqueued": len(work_units),
        "local_mode": local_mode,
        "work_units": work_units,
    }


def _get_sqs_client():
    import boto3

    return boto3.client("sqs")
