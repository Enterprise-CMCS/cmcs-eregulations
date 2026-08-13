"""eCFR worker entrypoint for single-part ingestion into eRegs.

Each invocation processes one title/part message, fetches current structure and
optionally full XML, derives location metadata, and uploads the final payload.
"""

import json
import logging
import os
from pathlib import Path

from .ecfr_client import fetch_part_full_xml, fetch_part_structure
from .config import parse_config_from_event
from .transforms import determine_part_depth, extract_sections_and_subparts, normalize_structure_for_upload
from .xml_parser import parse_part_xml_to_document


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, _context):
    """Process one queued eCFR part work unit end-to-end."""

    config = parse_config_from_event(event)

    logger.info(
        "Parsing eCFR work item: title=%s part=%s effective_date=%s",
        config.title_number,
        config.part_number,
        config.effective_date,
    )

    structure = fetch_part_structure(
        title_number=config.title_number,
        part_number=config.part_number,
    )
    structure = normalize_structure_for_upload(structure)
    depth = determine_part_depth(structure, config.part_number)

    document = {}
    if config.upload_reg_text:
        full_xml = fetch_part_full_xml(
            title_number=config.title_number,
            part_number=config.part_number,
            effective_date=config.effective_date,
        )
        document = parse_part_xml_to_document(
            full_xml,
            title_number=config.title_number,
            part_number=config.part_number,
        )

    sections = []
    subparts = []
    if config.upload_locations:
        sections, subparts = extract_sections_and_subparts(structure, config.part_number)

    part_payload = {
        "name": str(config.part_number),
        "title": str(config.title_number),
        "date": config.effective_date,
        "document": document,
        "structure": structure,
        "depth": depth,
        "sections": sections,
        "subparts": subparts,
    }

    output_path = _write_debug_payload(
        part_payload,
        title_number=config.title_number,
        part_number=config.part_number,
        effective_date=config.effective_date,
    )

    logger.info(
        "Wrote eCFR parsed payload: title=%s part=%s sections=%s subparts=%s path=%s",
        config.title_number,
        config.part_number,
        len(sections),
        len(subparts),
        output_path,
    )

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(
            {
                "processed": 1,
                "title_number": config.title_number,
                "part_number": config.part_number,
                "effective_date": config.effective_date,
                "uploaded": False,
                "output_path": str(output_path),
            }
        ),
    }


def _write_debug_payload(payload: dict, title_number: int, part_number: int, effective_date: str) -> Path:
    """Persist parsed part payload to disk for local inspection/debugging."""

    output_dir = Path(os.environ.get("PARSER_DEBUG_OUTPUT_DIR", "/tmp/ecfr-worker-output"))
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_date = effective_date.replace("/", "-")
    output_path = output_dir / f"title-{title_number}_part-{part_number}_{safe_date}.json"
    output_path.write_text(json.dumps(payload, indent=4), encoding="utf-8")
    return output_path
