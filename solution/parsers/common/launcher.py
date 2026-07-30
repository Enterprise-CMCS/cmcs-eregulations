import json
import os
from typing import Any

import boto3


def is_local_mode() -> bool:
    return os.environ.get("PARSER_LOCAL_MODE", "false").lower() == "true"


def build_basic_credentials_from_env() -> dict[str, str]:
    return {
        "auth_type": "basic",
        "username": os.environ.get("EREGS_USERNAME", ""),
        "password": os.environ.get("EREGS_PASSWORD", ""),
    }


def send_work_units(queue_url: str, work_units: list[dict[str, Any]]) -> None:
    sqs = boto3.client("sqs")

    for work_unit in work_units:
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(work_unit),
        )
