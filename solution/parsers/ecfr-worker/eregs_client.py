from typing import Any
from urllib.parse import urljoin

import requests

from common.auth import BackendCredentials, build_auth_headers
from common.config import ConfigParseError


class EregsClientError(RuntimeError):
    pass


REQUIRED_PART_FIELDS = (
    "name",
    "title",
    "date",
    "document",
    "structure",
    "depth",
    "sections",
    "subparts",
)


def upload_part(
    api_base_url: str,
    credentials: BackendCredentials,
    payload: dict[str, Any],
    timeout: int = 60,
) -> dict[str, Any]:
    _validate_part_payload(payload)

    request_url = urljoin(api_base_url, "part")
    try:
        headers = build_auth_headers(credentials)
    except ConfigParseError as exc:
        raise EregsClientError(str(exc)) from exc

    headers["Content-Type"] = "application/json"

    try:
        response = requests.put(request_url, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "unknown"
        raise EregsClientError(f"eRegs part upload failed ({status_code})") from exc
    except requests.RequestException as exc:
        raise EregsClientError(f"eRegs part upload request failed: {exc}") from exc

    if not response.text.strip():
        return {}

    try:
        response_payload = response.json()
    except ValueError as exc:
        raise EregsClientError("eRegs part upload response was not valid JSON") from exc

    if not isinstance(response_payload, dict):
        raise EregsClientError("eRegs part upload response must be a JSON object")

    return response_payload


def _validate_part_payload(payload: Any) -> None:
    if not isinstance(payload, dict):
        raise EregsClientError("part upload payload must be a JSON object")

    missing = [field for field in REQUIRED_PART_FIELDS if field not in payload]
    if missing:
        raise EregsClientError(f"part upload payload missing required fields: {', '.join(missing)}")
