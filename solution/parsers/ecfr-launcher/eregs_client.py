"""HTTP client helpers for writing eCFR launcher run results to eRegs."""

from typing import Any

from common.eregs_client import send_json

from common.auth import BackendCredentials


def create_ecfr_launcher_result(
    api_base_url: str,
    credentials: BackendCredentials,
    payload: dict[str, Any],
    timeout: int = 60,
) -> dict[str, Any]:
    """Create one eCFR launcher result entry at /v3/parsers/ecfr/launcher-results."""

    return send_json(
        api_base_url,
        "post",
        "parsers/ecfr/launcher-results",
        credentials,
        "eRegs eCFR launcher result upload",
        json_body=payload,
        timeout=timeout,
    )


def update_ecfr_launcher_result(
    api_base_url: str,
    credentials: BackendCredentials,
    payload: dict[str, Any],
    timeout: int = 60,
) -> dict[str, Any]:
    """Update the latest eCFR launcher result entry at /v3/parsers/ecfr/launcher-results."""

    return send_json(
        api_base_url,
        "patch",
        "parsers/ecfr/launcher-results",
        credentials,
        "eRegs eCFR launcher result update",
        json_body=payload,
        timeout=timeout,
    )
