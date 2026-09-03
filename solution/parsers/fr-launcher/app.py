"""Federal Register launcher entrypoint for queueing document-level parser work.

This Lambda reads parser_config from eRegs, expands upload_fr_docs-enabled
part targets, discovers Federal Register documents per title/part, deduplicates
against already-processed documents when skip_fr_documents is enabled, then
sends one work unit per document to SQS (or local worker HTTP in dev mode).
After queueing it records a counts-only FrLauncherResult run entry.
"""

import logging
import os
from typing import Any

from common.config import require_bool_config
from common.eregs_config import fetch_parser_config
from common.launcher import (
    build_launcher_response,
    dispatch_work_units,
    is_local_mode,
)
from common.logging import resolve_parser_log_level

from common.auth import resolve_backend_credentials

from .eregs_client import (
    create_fr_launcher_result,
    fetch_existing_document_numbers,
)
from .fedreg_client import FrDoc, fetch_documents
from .frlaunch_config import FrTarget, expand_fr_targets

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_ECFR_API_BASE_URL_ENV_VAR = "ECFR_API_BASE_URL"
_DEFAULT_ECFR_API_BASE_URL = "https://www.ecfr.gov/api/versioner/v1/"
_FEDERAL_REGISTER_API_BASE_URL_ENV_VAR = "FEDERAL_REGISTER_API_BASE_URL"


def _resolve_skip_fr_documents(parser_config: dict[str, Any]) -> bool:
    """Resolve skip_fr_documents from parser-config."""

    return require_bool_config(parser_config, "skip_fr_documents")


def _resolve_ecfr_api_base_url() -> str:
    """Resolve eCFR API base URL from environment with production default."""

    return os.getenv(_ECFR_API_BASE_URL_ENV_VAR, _DEFAULT_ECFR_API_BASE_URL)


def _resolve_fr_api_base_url() -> str:
    """Resolve Federal Register API base URL from environment."""

    return os.environ.get(_FEDERAL_REGISTER_API_BASE_URL_ENV_VAR) or "https://www.federalregister.gov"


def _build_work_units(
    parser_config: dict[str, Any],
    api_base_url: str,
    credentials,
    parser_log_level: str,
    ecfr_api_base_url: str,
    fr_api_base_url: str,
) -> tuple[list[dict[str, Any]], int]:
    """Discover FR documents and build one worker message per document.

    Returns valid work units and the total number of documents skipped due to
    deduplication.
    """

    targets = expand_fr_targets(parser_config, ecfr_base_url=ecfr_api_base_url)
    skip_fr_documents = _resolve_skip_fr_documents(parser_config)
    existing: set[str] = set()
    if skip_fr_documents:
        existing = set(fetch_existing_document_numbers(api_base_url=api_base_url, credentials=credentials))

    work_units: list[dict[str, Any]] = []
    skipped_count = 0
    for target in targets:
        docs = fetch_documents(title=target.title_number, part=str(target.part_number), base_url=fr_api_base_url)
        for doc in docs:
            if skip_fr_documents and doc.document_number in existing:
                skipped_count += 1
                continue
            work_units.append(_build_work_unit(doc, target, parser_log_level))

    return work_units, skipped_count


def _build_work_unit(doc: FrDoc, target: FrTarget, parser_log_level: str) -> dict[str, Any]:
    """Build a single worker message from one FR document."""

    return {
        "config": {
            "document_number": doc.document_number,
            "title": target.title_number,
            "part": str(target.part_number),
            "description": doc.description,
            "name": doc.name,
            "doc_type": doc.category,
            "url": doc.url,
            "date": doc.date,
            "docket_numbers": doc.docket_numbers,
            "raw_text_url": doc.raw_text_url,
            "full_text_xml_url": doc.full_text_url,
            "log_level": parser_log_level,
        }
    }


def handler(event, _context):
    """Main launcher handler for scheduled/on-demand FR work generation."""

    logger.info(
        "FR launcher trigger received: keys=%s has_records=%s has_body=%s",
        sorted(event.keys()) if isinstance(event, dict) else "non-dict",
        isinstance(event, dict) and isinstance(event.get("Records"), list),
        isinstance(event, dict) and "body" in event,
    )

    credentials = resolve_backend_credentials()
    logger.info("FR launcher credentials resolved with auth_type=%s", credentials.auth_type)

    api_base_url = os.environ["EREGS_API_URL_V3"]
    ecfr_api_base_url = _resolve_ecfr_api_base_url()
    fr_api_base_url = _resolve_fr_api_base_url()
    parser_config = fetch_parser_config(api_base_url=api_base_url, credentials=credentials)
    parser_log_level = resolve_parser_log_level(parser_config)
    logger.setLevel(getattr(logging, parser_log_level))
    logger.info("FR launcher parser-config loglevel resolved: %s", parser_log_level)

    try:
        work_units, skipped_count = _build_work_units(
            parser_config=parser_config,
            api_base_url=api_base_url,
            credentials=credentials,
            parser_log_level=parser_log_level,
            ecfr_api_base_url=ecfr_api_base_url,
            fr_api_base_url=fr_api_base_url,
        )

        if work_units:
            local_mode, succeeded, dispatch_failures = dispatch_work_units(work_units)
        else:
            local_mode = is_local_mode()
            succeeded = 0
            dispatch_failures = []

        if local_mode:
            logger.info("FR launcher sent %s/%s work unit(s) to local worker", succeeded, len(work_units))
        else:
            logger.info("FR launcher enqueued %s work unit(s)", len(work_units))

        create_fr_launcher_result(
            api_base_url=api_base_url,
            credentials=credentials,
            payload={
                "success": True,
                "log": f"queued={len(work_units)} skipped={skipped_count} dispatch_failed={len(dispatch_failures)}",
                "queued_count": len(work_units),
                "skipped_count": skipped_count,
                "failed_count": len(dispatch_failures),
            },
        )
        logger.info(
            "FR launcher result recorded: queued=%s skipped=%s dispatch_failed=%s",
            len(work_units),
            skipped_count,
            len(dispatch_failures),
        )

        return build_launcher_response(
            work_units=work_units,
            local_mode=local_mode,
            succeeded=succeeded,
            failures=dispatch_failures,
        )
    except Exception as exc:
        logger.error("FR launcher failed: %s", exc)
        try:
            create_fr_launcher_result(
                api_base_url=api_base_url,
                credentials=credentials,
                payload={"success": False, "log": str(exc)},
            )
        except Exception as log_exc:
            logger.warning("Failed to record FR launcher failure result: %s", log_exc)
        raise
