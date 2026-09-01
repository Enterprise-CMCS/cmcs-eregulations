"""HTTP client helpers for uploading Federal Register documents to eRegs.

The FR worker builds a FederalRegisterLink payload (document metadata plus
extracted section/range locations) and PUTs it to eRegs. It also posts per
document parser results under the parsers FR results endpoint. Shared
EregsClientError and the generic send_json client live in common.eregs_client.
"""

from typing import Any

from common.eregs_client import EregsClientError, send_json

from common.auth import BackendCredentials

REQUIRED_DOCUMENT_FIELDS = (
    "name",
    "description",
    "doc_type",
    "url",
    "date",
    "document_number",
)


def upload_fr_document(
    api_base_url: str,
    credentials: BackendCredentials,
    payload: dict[str, Any],
    timeout: int = 60,
) -> dict[str, Any]:
    """Upload one Federal Register document payload to eRegs."""

    _validate_document_payload(payload)

    return send_json(
        api_base_url,
        "put",
        "resources/public/federal_register_links",
        credentials,
        "eRegs Federal Register document upload",
        json_body=payload,
        timeout=timeout,
    )


def create_fr_result(
    api_base_url: str,
    credentials: BackendCredentials,
    payload: dict[str, Any],
    timeout: int = 60,
) -> dict[str, Any]:
    """Create one Federal Register parser result entry at /v3/parsers/fr/results."""

    return send_json(
        api_base_url,
        "post",
        "parsers/fr/results",
        credentials,
        "eRegs FR result upload",
        json_body=payload,
        timeout=timeout,
    )


def _validate_document_payload(payload: Any) -> None:
    """Validate required top-level keys for Federal Register document uploads."""

    if not isinstance(payload, dict):
        raise EregsClientError("Federal Register document payload must be a JSON object")

    missing = [field for field in REQUIRED_DOCUMENT_FIELDS if field not in payload]
    if missing:
        raise EregsClientError(
            f"Federal Register document payload missing required fields: {', '.join(missing)}"
        )
