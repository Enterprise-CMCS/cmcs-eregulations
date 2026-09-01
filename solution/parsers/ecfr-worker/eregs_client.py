"""HTTP client helpers for uploading parsed part payloads to eRegs.

The eCFR worker builds normalized part payloads and delegates outbound upload
behavior to this module. Shared per-part result-row writes live in
common.eregs_client.
"""

from typing import Any

from common.eregs_client import EregsClientError, send_json

from common.auth import BackendCredentials

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
    """Upload one parsed part payload to eRegs /v3/parsers/ecfr/parts."""

    _validate_part_payload(payload)

    return send_json(
        api_base_url,
        "put",
        "parsers/ecfr/parts",
        credentials,
        "eRegs part upload",
        json_body=payload,
        timeout=timeout,
    )


def _validate_part_payload(payload: Any) -> None:
    """Validate required top-level keys for part upload payloads."""

    if not isinstance(payload, dict):
        raise EregsClientError("part upload payload must be a JSON object")

    missing = [field for field in REQUIRED_PART_FIELDS if field not in payload]
    if missing:
        raise EregsClientError(f"part upload payload missing required fields: {', '.join(missing)}")
