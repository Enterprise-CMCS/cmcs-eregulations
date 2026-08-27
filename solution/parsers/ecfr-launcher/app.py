"""eCFR launcher entrypoint for queueing part-level parser work.

This Lambda reads parser_config from eRegs, expands part targets (including
subchapters), resolves latest per-part effective dates from eCFR, then sends
work units to SQS (or local worker HTTP in dev mode).
"""

import json
import logging
import os
from typing import Any

from common.auth import resolve_backend_credentials
from common.config import ConfigParseError, require_bool, require_non_empty_string
from common.launcher import (
    build_launcher_response,
    dispatch_work_units,
    is_local_mode,
)
from common.logging import resolve_log_level_name

from .eregs_config import (
    TargetPartConfig,
    expand_target_parts,
    fetch_existing_part_dates_by_title,
    fetch_parser_config,
)
from .eregs_client import create_ecfr_launcher_result
from .ecfr_versions import fetch_title_versions, latest_issue_dates_by_part


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


_ECFR_API_BASE_URL_ENV_VAR = "ECFR_API_BASE_URL"
_DEFAULT_ECFR_API_BASE_URL = "https://www.ecfr.gov/api/versioner/v1/"


def _resolve_ecfr_api_base_url() -> str:
    """Resolve eCFR API base URL from environment with production default."""

    return os.getenv(_ECFR_API_BASE_URL_ENV_VAR, _DEFAULT_ECFR_API_BASE_URL)


def _build_work_units(
    parser_config: dict[str, Any],
    api_base_url: str,
    credentials,
    ecfr_api_base_url: str,
    parser_log_level: str,
) -> tuple[list[dict], list[dict[str, str]]]:
    """Build worker messages from parser config and latest-date resolution.

    Returns both valid work units and per-part failures for targets that cannot
    be queued (for example, no resolvable latest date).
    """

    targets = expand_target_parts(parser_config, ecfr_base_url=ecfr_api_base_url)
    latest_dates_by_title = _resolve_latest_dates_by_title(targets, ecfr_api_base_url)
    skip_parsed_regs = _resolve_skip_parsed_regs(parser_config)
    upload_supplemental_locations = _resolve_upload_supplemental_locations(parser_config)
    existing_dates_by_title = (
        _resolve_existing_part_dates_by_title(api_base_url, credentials, targets)
        if skip_parsed_regs
        else {}
    )

    work_units: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for target in targets:
        latest_issue_date = latest_dates_by_title.get(target.title_number, {}).get(target.part_number)
        if latest_issue_date is None:
            failures.append(
                {
                    "title_number": str(target.title_number),
                    "part_number": str(target.part_number),
                    "reason": "No latest issue_date available for part",
                }
            )
            continue

        existing_date = existing_dates_by_title.get(target.title_number, {}).get(target.part_number)
        if existing_date == latest_issue_date:
            logger.info(
                "Skipping previously parsed part: title=%s part=%s date=%s",
                target.title_number,
                target.part_number,
                latest_issue_date,
            )
            continue

        upload_locations = target.upload_locations and upload_supplemental_locations

        work_units.append(
            {
                "config": {
                    "title_number": target.title_number,
                    "part_number": target.part_number,
                    "effective_date": latest_issue_date,
                    "upload_reg_text": target.upload_reg_text,
                    "upload_locations": upload_locations,
                    "log_level": parser_log_level,
                }
            }
        )

    return work_units, failures


def _resolve_existing_part_dates_by_title(
    api_base_url: str,
    credentials,
    targets: list[TargetPartConfig],
) -> dict[int, dict[int, str]]:
    """Fetch existing eRegs part issue dates for all requested titles."""

    by_title: dict[int, dict[int, str]] = {}
    title_numbers = sorted({target.title_number for target in targets})
    for title_number in title_numbers:
        by_title[title_number] = fetch_existing_part_dates_by_title(
            api_base_url=api_base_url,
            credentials=credentials,
            title_number=title_number,
        )
    return by_title


def _resolve_latest_dates_by_title(targets: list[TargetPartConfig], ecfr_api_base_url: str) -> dict[int, dict[int, str]]:
    """Resolve latest effective date per requested part, grouped by title.

    This uses one title-level versions API call (with pagination) and builds a
    compact lookup map consumed by _build_work_units.
    """

    by_title: dict[int, dict[int, str]] = {}
    title_numbers = sorted({target.title_number for target in targets})

    for title_number in title_numbers:
        versions_payload = fetch_title_versions(title_number=title_number, base_url=ecfr_api_base_url)
        latest_by_part = latest_issue_dates_by_part(versions_payload)

        by_part_number: dict[int, str] = {}
        for part_raw, latest_issue_date in latest_by_part.items():
            if part_raw.isdigit():
                by_part_number[int(part_raw)] = latest_issue_date

        requested_parts = sorted({target.part_number for target in targets if target.title_number == title_number})
        if requested_parts:
            available_parts = sorted(by_part_number.keys())
            missing_parts = [part for part in requested_parts if part not in by_part_number]
            logger.info(
                "eCFR versions resolved for title=%s available_parts=%s requested_parts=%s missing_parts=%s",
                title_number,
                len(available_parts),
                len(requested_parts),
                len(missing_parts),
            )

        by_title[title_number] = by_part_number

    return by_title


def _resolve_parser_log_level(parser_config: dict[str, Any]) -> str:
    """Resolve and validate parser log level from parser-config."""

    try:
        configured = require_non_empty_string(parser_config, "loglevel")
        return resolve_log_level_name(configured)
    except ConfigParseError as exc:
        raise RuntimeError(str(exc)) from exc


def _resolve_skip_parsed_regs(parser_config: dict[str, Any]) -> bool:
    """Resolve skip_parsed_regs from parser-config."""

    try:
        return require_bool(parser_config, "skip_parsed_regs")
    except ConfigParseError as exc:
        raise RuntimeError(str(exc)) from exc


def _resolve_upload_supplemental_locations(parser_config: dict[str, Any]) -> bool:
    """Resolve global upload_supplemental_locations override from parser-config."""

    try:
        return require_bool(parser_config, "upload_supplemental_locations")
    except ConfigParseError as exc:
        raise RuntimeError(str(exc)) from exc


def handler(event, _context):
    """Main launcher handler for scheduled/on-demand eCFR work generation."""

    logger.info(
        "eCFR launcher trigger received: keys=%s has_records=%s has_body=%s",
        sorted(event.keys()) if isinstance(event, dict) else "non-dict",
        isinstance(event, dict) and isinstance(event.get("Records"), list),
        isinstance(event, dict) and "body" in event,
    )

    credentials = resolve_backend_credentials()
    logger.info("eCFR launcher credentials resolved with auth_type=%s", credentials.auth_type)

    api_base_url = os.environ["EREGS_API_URL_V3"]
    ecfr_api_base_url = _resolve_ecfr_api_base_url()
    parser_config = fetch_parser_config(api_base_url=api_base_url, credentials=credentials)
    parser_log_level = _resolve_parser_log_level(parser_config)
    logger.setLevel(getattr(logging, parser_log_level))
    logger.info("eCFR launcher parser-config loglevel resolved: %s", parser_log_level)

    try:
        work_units, config_failures = _build_work_units(
            parser_config=parser_config,
            api_base_url=api_base_url,
            credentials=credentials,
            ecfr_api_base_url=ecfr_api_base_url,
            parser_log_level=parser_log_level,
        )

        if not work_units and config_failures:
            raise RuntimeError(
                f"eCFR launcher could not enqueue any work units; {len(config_failures)} part(s) missing latest issue_date"
            )

        if work_units:
            local_mode, succeeded, dispatch_failures = dispatch_work_units(work_units)
        else:
            local_mode = is_local_mode()
            succeeded = 0
            dispatch_failures = []

        failures = config_failures + dispatch_failures
        if local_mode:
            logger.info("eCFR launcher sent %s/%s work unit(s) to local worker", succeeded, len(work_units))
        else:
            logger.info("eCFR launcher enqueued %s work unit(s)", len(work_units))

        if config_failures:
            logger.warning("eCFR launcher skipped %s work unit(s) due to missing latest issue_date", len(config_failures))

        logger.debug("Uploading eCFR launcher success result")
        create_ecfr_launcher_result(
            api_base_url=api_base_url,
            credentials=credentials,
            payload={"success": True, "log": ""},
        )
        logger.debug("Uploaded eCFR launcher success result")

        return build_launcher_response(
            work_units=work_units,
            local_mode=local_mode,
            succeeded=succeeded,
            failures=failures,
        )
    except Exception as exc:
        logger.error("eCFR launcher failed: %s", exc)
        try:
            logger.debug("Uploading eCFR launcher failure result")
            create_ecfr_launcher_result(
                api_base_url=api_base_url,
                credentials=credentials,
                payload={"success": False, "log": str(exc)},
            )
            logger.debug("Uploaded eCFR launcher failure result")
        except Exception as log_exc:
            logger.warning("Failed to record eCFR launcher failure result: %s", log_exc)
        raise
