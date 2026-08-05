import json
import logging
import os

try:
    from .ecfr_client import fetch_part_full_xml, fetch_part_structure
    from .eregs_client import upload_part
    from .config import parse_config_from_event
    from .transform import determine_part_depth, extract_sections_and_subparts
except ImportError as exc:
    if __package__:
        raise
    from ecfr_client import fetch_part_full_xml, fetch_part_structure
    from eregs_client import upload_part
    from config import parse_config_from_event
    from transform import determine_part_depth, extract_sections_and_subparts


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, _context):
    config = parse_config_from_event(event)

    logger.info(
        "Parsed eCFR work item: title=%s part=%s effective_date=%s",
        config.title_number,
        config.part_number,
        config.effective_date,
    )

    structure = fetch_part_structure(
        title_number=config.title_number,
        part_number=config.part_number,
    )
    depth = determine_part_depth(structure, config.part_number)

    document = {}
    if config.upload_reg_text:
        full_xml = fetch_part_full_xml(
            title_number=config.title_number,
            part_number=config.part_number,
            effective_date=config.effective_date,
        )
        document = {"raw_xml": full_xml}

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

    api_base_url = os.environ["EREGS_API_URL_V3"]
    upload_result = upload_part(
        api_base_url=api_base_url,
        credentials=config.credentials,
        payload=part_payload,
    )

    logger.info(
        "Uploaded eCFR part to eRegs: title=%s part=%s sections=%s subparts=%s",
        config.title_number,
        config.part_number,
        len(sections),
        len(subparts),
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
                "uploaded": True,
                "upload_result_keys": sorted(upload_result.keys()),
            }
        ),
    }
