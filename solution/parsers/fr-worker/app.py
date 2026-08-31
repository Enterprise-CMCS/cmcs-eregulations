"""Federal Register worker entrypoint for single-document ingestion into eRegs.

Each invocation processes exactly one Federal Register document message: it
fetches the document's full-text XML (when available), extracts the referenced
CFR sections/ranges, uploads the document payload to eRegs, and records the
parse result.
"""

import json
import logging
import os
from dataclasses import asdict

from .config import FrDocumentConfig, parse_config_from_event
from .eregs_client import create_fr_result, upload_fr_document
from .fedreg_client import fetch_full_text_sections
from .links import create_section_ranges, create_sections

logger = logging.getLogger(__name__)


def _configure_logging(log_level_name: str | None = None) -> None:
    """Configure root logging for worker execution."""

    if log_level_name is None:
        log_level_name = "INFO"

    log_level = getattr(logging, log_level_name, logging.INFO)
    logging.basicConfig(level=log_level)
    logger.setLevel(log_level)


_configure_logging()


def _extract_linked_sections(config: FrDocumentConfig) -> tuple[list, list]:
    """Fetch FR full text and build section/range links, keeping failures non-fatal.

    Mirrors the old FR parser: when no full-text XML URL is available, or
    fetching/extracting sections fails, the document is still uploaded — just
    without section linkage.
    """

    if not config.full_text_xml_url:
        logger.warning(
            "No full text XML available for FR doc %s; uploading without section links",
            config.document_number,
        )
        return [], []

    logger.info(
        "Fetching full text sections for FR doc %s",
        config.document_number,
    )
    sections, section_ranges, part_map = fetch_full_text_sections(
        config.full_text_xml_url,
        titles={str(config.title)},
    )
    logger.debug(
        "Extracted section tokens: %s, range tokens: %s, part map keys: %s",
        len(sections),
        len(section_ranges),
        sorted(part_map.keys()),
    )

    return create_sections(sections, part_map), create_section_ranges(section_ranges, part_map)


def _process_work_item(config: FrDocumentConfig) -> dict:
    """Run the FR document pipeline and return the lambda success response body."""

    logger.debug("Building Federal Register document upload payload")
    document_payload = {
        "name": config.name,
        "description": config.description,
        "doc_type": config.doc_type,
        "url": config.url,
        "date": config.date,
        "docket_numbers": config.docket_numbers,
        "document_number": config.document_number,
        "raw_text_url": config.raw_text_url,
    }

    link_sections, link_ranges = [], []
    try:
        link_sections, link_ranges = _extract_linked_sections(config)
    except Exception as exc:
        logger.error(
            "Failed to extract linked sections for FR doc %s: %s",
            config.document_number,
            exc,
        )

    logger.info("Uploading Federal Register document to eRegs: document_number=%s", config.document_number)
    document_payload["sections"] = [asdict(s) for s in link_sections]
    document_payload["section_ranges"] = [asdict(r) for r in link_ranges]
    upload_result = upload_fr_document(
        api_base_url=os.environ["EREGS_API_URL_V3"],
        credentials=config.credentials,
        payload=document_payload,
    )
    logger.debug("Upload response keys=%s", sorted(upload_result.keys()))

    logger.info(
        "Uploaded Federal Register document: document_number=%s sections=%s ranges=%s",
        config.document_number,
        len(link_sections),
        len(link_ranges),
    )

    return {
        "processed": 1,
        "document_number": config.document_number,
        "sections": len(link_sections),
        "section_ranges": len(link_ranges),
        "uploaded": True,
        "upload_result_keys": sorted(upload_result.keys()),
    }


def handler(event, _context):
    """Process one queued Federal Register document work unit end-to-end."""

    event_keys = sorted(event.keys()) if isinstance(event, dict) else []
    logger.info(
        "Starting FR worker invocation: keys=%s has_records=%s has_body=%s",
        event_keys,
        isinstance(event, dict) and "Records" in event,
        isinstance(event, dict) and "body" in event,
    )
    logger.debug("Resolving work item config from invocation event")

    config = parse_config_from_event(event)
    _configure_logging(config.log_level)

    logger.info(
        "Parsing FR work item: document_number=%s title=%s part=%s",
        config.document_number,
        config.title,
        config.part,
    )

    try:
        body = _process_work_item(config)
        logger.debug("Posting FR parser success result for document_number=%s", config.document_number)
        create_fr_result(
            api_base_url=os.environ["EREGS_API_URL_V3"],
            credentials=config.credentials,
            payload={
                "success": True,
                "log": "",
                "document_number": config.document_number,
            },
        )
        logger.debug("Posted FR parser success result for document_number=%s", config.document_number)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps(body),
        }
    except Exception as exc:
        logger.error(
            "FR worker failed: document_number=%s error=%s",
            config.document_number,
            exc,
        )
        try:
            logger.debug(
                "Posting FR parser failure result for document_number=%s",
                config.document_number,
            )
            create_fr_result(
                api_base_url=os.environ["EREGS_API_URL_V3"],
                credentials=config.credentials,
                payload={
                    "success": False,
                    "log": str(exc),
                    "document_number": config.document_number,
                },
            )
            logger.debug(
                "Posted FR parser failure result for document_number=%s",
                config.document_number,
            )
        except Exception as log_exc:
            logger.warning("Failed to record FR worker failure result: %s", log_exc)
        raise
