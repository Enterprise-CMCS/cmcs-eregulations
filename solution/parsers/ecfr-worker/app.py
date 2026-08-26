"""eCFR worker entrypoint for single-part ingestion into eRegs.

Each invocation processes one title/part message, fetches current structure and
optionally full XML, derives location metadata, and uploads the final payload.
"""

import json
import logging
import os

from .ecfr_client import fetch_part_full_xml, fetch_part_structure
from .config import EcfrPartConfig, parse_config_from_event
from .eregs_client import create_ecfr_result, upload_part
from .transforms import determine_part_depth, extract_sections_and_subparts, normalize_structure_for_upload
from .xml_parser import parse_part_xml_to_document


logger = logging.getLogger(__name__)

_ECFR_API_BASE_URL_ENV_VAR = "ECFR_API_BASE_URL"
_DEFAULT_ECFR_API_BASE_URL = "https://www.ecfr.gov/api/versioner/v1/"

def _configure_logging(log_level_name: str | None = None) -> None:
    """Configure root logging for worker execution."""

    if log_level_name is None:
        log_level_name = "INFO"

    log_level = getattr(logging, log_level_name, logging.INFO)
    logging.basicConfig(level=log_level)
    logger.setLevel(log_level)


def _resolve_ecfr_api_base_url() -> str:
    """Resolve eCFR API base URL from environment with production default."""

    return os.getenv(_ECFR_API_BASE_URL_ENV_VAR, _DEFAULT_ECFR_API_BASE_URL)


_configure_logging()


def _process_work_item(config: EcfrPartConfig) -> dict:
    """Run the eCFR parsing pipeline and return the lambda success response body."""

    ecfr_api_base_url = _resolve_ecfr_api_base_url()
    logger.debug("Resolved eCFR API base URL=%s", ecfr_api_base_url)

    logger.info("Fetching part structure from eCFR API")
    structure = fetch_part_structure(
        title_number=config.title_number,
        part_number=config.part_number,
        base_url=ecfr_api_base_url,
    )
    logger.debug("Normalizing structure payload for upload")
    structure = normalize_structure_for_upload(structure)
    logger.debug("Determining part depth from normalized structure")
    depth = determine_part_depth(structure, config.part_number)
    logger.info("Resolved part depth=%s", depth)

    document = {}
    if config.upload_reg_text:
        logger.info("Fetching full XML for regulation text parsing")
        full_xml = fetch_part_full_xml(
            title_number=config.title_number,
            part_number=config.part_number,
            effective_date=config.effective_date,
            base_url=ecfr_api_base_url,
        )
        logger.debug("Parsing full XML into normalized eRegs document")
        document = parse_part_xml_to_document(
            full_xml,
            title_number=config.title_number,
            part_number=config.part_number,
        )
        logger.debug("Parsed document top-level keys=%s", sorted(document.keys()))
    else:
        logger.info("Skipping regulation text parsing (upload_reg_text=false)")

    sections = []
    subparts = []
    if config.upload_locations:
        logger.info("Extracting section and subpart locations from structure")
        sections, subparts = extract_sections_and_subparts(structure, config.part_number)
        logger.debug("Extracted locations: sections=%s subparts=%s", len(sections), len(subparts))
    else:
        logger.info("Skipping location extraction (upload_locations=false)")

    logger.debug("Building part upload payload")
    part_payload = {
        "name": str(config.part_number),
        "title": str(config.title_number),
        "date": config.effective_date,
        "document": document,
        "structure": structure,
        "depth": depth,
        "sections": sections,
        "subparts": subparts,
        "upload_reg_text": config.upload_reg_text,
        "upload_locations": config.upload_locations,
    }

    logger.info("Uploading parsed part payload to eRegs")
    upload_result = upload_part(
        api_base_url=os.environ["EREGS_API_URL_V3"],
        credentials=config.credentials,
        payload=part_payload,
    )
    logger.debug("Upload response keys=%s", sorted(upload_result.keys()))

    logger.debug(
        "Uploading eCFR success result: title=%s part=%s date=%s",
        config.title_number,
        config.part_number,
        config.effective_date,
    )
    create_ecfr_result(
        api_base_url=os.environ["EREGS_API_URL_V3"],
        credentials=config.credentials,
        payload={
            "success": True,
            "log": "",
            "title": config.title_number,
            "part": config.part_number,
            "date": config.effective_date,
        },
    )
    logger.debug("Uploaded eCFR success result")

    logger.info(
        "Uploaded eCFR parsed payload: title=%s part=%s sections=%s subparts=%s",
        config.title_number,
        config.part_number,
        len(sections),
        len(subparts),
    )

    return {
        "processed": 1,
        "title_number": config.title_number,
        "part_number": config.part_number,
        "effective_date": config.effective_date,
        "uploaded": True,
        "upload_result_keys": sorted(upload_result.keys()),
    }


def handler(event, _context):
    """Process one queued eCFR part work unit end-to-end."""

    event_keys = sorted(event.keys()) if isinstance(event, dict) else []
    logger.info(
        "Starting eCFR worker invocation: keys=%s has_records=%s has_body=%s",
        event_keys,
        isinstance(event, dict) and "Records" in event,
        isinstance(event, dict) and "body" in event,
    )
    logger.debug("Resolving work item config from invocation event")

    config = parse_config_from_event(event)
    _configure_logging(config.log_level)

    logger.info(
        "Parsing eCFR work item: title=%s part=%s effective_date=%s",
        config.title_number,
        config.part_number,
        config.effective_date,
    )
    logger.debug(
        "Upload flags for work item: upload_reg_text=%s upload_locations=%s",
        config.upload_reg_text,
        config.upload_locations,
    )

    try:
        body = _process_work_item(config)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps(body),
        }
    except Exception as exc:
        logger.error(
            "eCFR worker failed: title=%s part=%s date=%s error=%s",
            config.title_number,
            config.part_number,
            config.effective_date,
            exc,
        )
        try:
            logger.debug(
                "Uploading eCFR failure result: title=%s part=%s date=%s",
                config.title_number,
                config.part_number,
                config.effective_date,
            )
            create_ecfr_result(
                api_base_url=os.environ["EREGS_API_URL_V3"],
                credentials=config.credentials,
                payload={
                    "success": False,
                    "log": str(exc),
                    "title": config.title_number,
                    "part": config.part_number,
                    "date": config.effective_date,
                },
            )
            logger.debug("Uploaded eCFR failure result")
        except Exception as log_exc:
            logger.warning("Failed to record eCFR worker failure result: %s", log_exc)
        raise
